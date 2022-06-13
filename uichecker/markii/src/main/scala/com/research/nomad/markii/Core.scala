/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii

import java.io.{FileWriter, PrintWriter}
import java.nio.file.{Files, Paths}

import com.research.nomad.markii.analyses.{ContextInsensitiveAnalysis, ContextSensitiveAnalysis, FlowInsensitiveAnalysis, PreVASCO}
import com.research.nomad.markii.dataflow.custom.{AbsFS, FromConfig}
import com.research.nomad.markii.dataflow.{AFTDomain, AbsValSet, AbstractValue, AbstractValuePropIFDS, CustomStatePropVASCO}
import com.research.nomad.markii.instrument.{AllInstrument, DialogCreateInstrument, DialogInitInstrument}
import heros.InterproceduralCFG
import heros.solver.IFDSSolver
import presto.android.gui.listener.EventType
import presto.android.{Configs, Debug}
import soot.jimple.Stmt
import soot.jimple.toolkits.ide.icfg.JimpleBasedInterproceduralCFG
import soot.{Local, Scene, SootClass, SootMethod, Value}
import vasco.{DataFlowSolution, Helper}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

case class Runner(method: SootMethod, loopExit: soot.Unit, view: Local)

/**
 * Core Analysis that implement the client interface IAnalysis
 */
class Core extends IAnalysis {
  // Constructor:
  private val analyzedMethods = mutable.Set[SootMethod]()
  private var outputPath = "/tmp/markii-facts/"
  var vascoMode = "context-sensitive,flow-sensitive"
  private var apiSemanticConfig: Option[String] = None
  private var debugMode = false
  def isDebugMode: Boolean = debugMode

  val icfg: JimpleBasedInterproceduralCFG = new JimpleBasedInterproceduralCFG()
  readConfigs() // FIXME: make it clear what data is read by this

  Files.deleteIfExists(Paths.get(outputPath + "/report.yaml"))
  appendYamlReport("pre_analysis_time_seconds", Debug.v().getExecutionTime)
  appendYamlReport("soot_get_classes_size", Scene.v().getClasses().size())
  appendYamlReport("soot_get_application_classes_size", Scene.v().getApplicationClasses().size())
  appendYamlReport("soot_get_application_classes", Scene.v().getApplicationClasses().asScala.map(_.getName))

  Ic3Manager.init()
  val appInfo = new AppInfo()
  Globals.appInfo = appInfo
  val controlFlowGraphManager = new ControlFlowGraphManager(appInfo)
  Globals.controlFlowGraphManager = controlFlowGraphManager

  appendYamlReport("hier_application_activity_classes_size", appInfo.hier.applicationActivityClasses.size())
  appendYamlReport("hier_application_activity_classes", appInfo.hier.applicationActivityClasses.asScala.map(_.getName))

  val dialogInitInstrument = new DialogInitInstrument(this)
  dialogInitInstrument.run()

  // TODO: use a proper harness
  val callGraphManager = new CallGraphManager(appInfo)

  private var ifdsSolver: IFDSSolver[soot.Unit, (Value, Set[AbstractValue]), SootMethod, InterproceduralCFG[soot.Unit, SootMethod]] = _

  private def _appendYamlReport(content: String): Unit = {
    Files.createDirectories(Paths.get(outputPath))
    val fileWriter = if (Files.exists(Paths.get(outputPath + "/report.yaml"))) {
      new FileWriter(outputPath + "/report.yaml", true)
    } else {
      new FileWriter(outputPath + "/report.yaml")
    }
    fileWriter.write(content + "\n")
    fileWriter.close()
  }

  private def appendYamlReport(key: String, value: Long): Unit = {
    _appendYamlReport(s"$key: $value")
  }

  private def appendYamlReport(key: String, value: String): Unit = {
    _appendYamlReport(s"$key: $value")
  }

  private def appendYamlReport(key: String, iterable: Iterable[String]): Unit = {
    _appendYamlReport(key + ":\n" + iterable.map(s => "    - " + s).mkString("\n"))
  }

  override def run(): Unit = {
    // IFDS must run before VASCO since VASCO depends on IFDS as pre-analysis
    runIFDS()

    val dialogCreateInstrument = new DialogCreateInstrument(this)
    dialogCreateInstrument.run(appInfo.allActivities)

    val allInstrument = new AllInstrument(this)
    allInstrument.run(appInfo.allActivities)

    val preVASCO = new PreVASCO(this, allInstrument, dialogCreateInstrument)

    // Write some constraints and prepare code for VASCO analysis
    for (handler <- appInfo.getAllHandlers) {
      preVASCO.analyze(handler)
    }

    for (activity <- appInfo.allActivities) {
      analyzeActivityPreVasco(activity)
    }

    val solution = runVASCO(preVASCO)

    val postAnalysis = new PostAnalysis(this, solution, outputPath, preVASCO)
    postAnalysis.run()

    if (apiSemanticConfig.nonEmpty) {
      runCustomVASCO(preVASCO, postAnalysis.writer)
    }

    // Dump abstractions
    if (isDebugMode) {
      dumpCallgraph()

      val ifdsPath = outputPath + "/ifds-abstractions.txt";
      println(s"Dump IFDS abstractions to: ${ifdsPath}")
      dumpIFDSAbstractions(ifdsPath)

      val vascoPath = outputPath + "/vasco-abstractions.json"
      println(s"Dump VASCO abstractions to: ${vascoPath}")
      Util.dumpVASCOAbstractions[AFTDomain](vascoPath,
        solution, x => x.nonEmpty, x => x.toJSONObj, analyzedMethods)
    }
  }


  private def dumpCallgraph(): Unit = {
    val destPath = "/tmp/call-graph.txt";
    println(s"Dump callgraph to: ${destPath}")
    val printWriter: PrintWriter = new PrintWriter(destPath)
    for (edge <- Scene.v().getCallGraph.asScala) {
      val source = edge.getSrc.method()
      if (analyzedMethods.contains(source) && !Configs.isLibraryClass(source.getDeclaringClass.getName)) {
        printWriter.println(edge.getSrc + "\n ==> " + edge.getTgt + "\n")
      }
    }
    printWriter.close()
  }


  private def runVASCO(preVasco: PreVASCO): DataFlowSolution[soot.Unit, AFTDomain] = {
    // NOTE: over-approx of entrypoints
    val entrypointsFull = appInfo.allActivities.flatMap(controlFlowGraphManager.getRunner).map(_.method).toList
    println(s"VASCO(${vascoMode}) starts")
    vascoMode match {
      case "context-sensitive,flow-sensitive" => {
        val vascoProp = ContextSensitiveAnalysis(this, preVasco, entrypointsFull)
        vascoProp.doAnalysis()

        analyzedMethods.addAll(appInfo.getAllHandlers)
        analyzedMethods.addAll(vascoProp.getMethods.asScala)

        if (sys.env.contains("BATCH_RUN")) {
          Helper.getMeetOverValidPathsSolution(vascoProp)
        } else {
          Helper.getMeetOverValidPathsSolutionPar(vascoProp)
        }
      }
      case "context-insensitive,flow-sensitive" => {
        val vascoProp = ContextInsensitiveAnalysis(this, preVasco, entrypointsFull)
        vascoProp.doAnalysis()

        analyzedMethods.addAll(appInfo.getAllHandlers)
        analyzedMethods.addAll(vascoProp.getMethods)

        vascoProp.getMeetOverValidPathsSolution
      }
      case "context-insensitive,flow-insensitive" => {
        val vascoProp = FlowInsensitiveAnalysis(this, preVasco, entrypointsFull)
        vascoProp.doAnalysis()

        analyzedMethods.addAll(appInfo.getAllHandlers)
        analyzedMethods.addAll(vascoProp.getMethods)

        vascoProp.getMeetOverValidPathsSolution
      }
    }
  }

  private def runCustomVASCO(preVasco: PreVASCO, writer: FactsWriter): Unit = {
    // NOTE: over-approx of entrypoints
    // FIXME: code duplication
    val entrypointsFull = appInfo.allActivities.flatMap(controlFlowGraphManager.getRunner).map(_.method).toList

    val eventHandlers =
      writer.getStoredFacts(FactsWriter.Fact.eventHandler).map(
        args => (args(1).asInstanceOf[SootMethod], args.head.asInstanceOf[EventType])).toMap ++
      writer.getStoredFacts(FactsWriter.Fact.enqueuedWorkRequest).map(
        args => (args(2).asInstanceOf[SootMethod], EventType.implicit_time_tick)).toMap

    val fromConfig = new FromConfig(apiSemanticConfig.get)
    val vascoProp = new CustomStatePropVASCO[AbsValSet[AbsFS]](this, preVasco, entrypointsFull ++ eventHandlers.keys.toList, fromConfig)
    println("VASCO starts")
    vascoProp.doAnalysis()
    println("VASCO finishes")

    for ((handler, eventType) <- eventHandlers) {
      val reachedMethods = callGraphManager.reachableMethods(handler)
      for (reached <- reachedMethods) {
        if (reached.getDeclaringClass.isApplicationClass && reached.isConcrete && reached.hasActiveBody) {
          for ((ref, prevState, postState) <- fromConfig.getTransitions(reached)) {
            val refStr = ref match {
              case Some(r) => r.toString
              case None => "unknown"
            }
            writer.writeFact(FactsWriter.Fact.apiStateTransition, handler, eventType, reached, refStr, prevState, postState)
          }
        }
      }
    }
  }

  private def readConfigs(): Unit = {
    for (param <- Configs.clientParams.asScala) {
      if (param.startsWith("output:")) outputPath = param.substring("output:".length)
      if (param.startsWith("vascoMode:")) vascoMode = param.substring("vascoMode:".length)
      if (param.startsWith("apiSemanticConfig:")) apiSemanticConfig = Some(param.substring("apiSemanticConfig:".length))
    }

    debugMode = sys.env.contains("DEBUG")
  }

  private def dumpIFDSAbstractions(outputPath: String): Unit = {
    val printWriter = new PrintWriter(outputPath)
    for (m <- analyzedMethods) {
      printWriter.println("====== Method " + m.getSignature + " =======")
      printWriter.println(m.getActiveBody)
      for (unit <- m.getActiveBody.getUnits.asScala) {
        val abstractions = ifdsSolver.ifdsResultsAt(unit)
        if (abstractions != null && abstractions.size() > 0) {
          for (value <- abstractions.asScala) {
            for (abstraction <- value._2) {
              printWriter.println("\t\t" + value._1 + ": " + abstraction)
            }
          }
          printWriter.println()
        }
      }
    }
    printWriter.close()
  }

  private def runIFDS(): Unit = {
    val analysis = new AbstractValuePropIFDS(this)
    ifdsSolver = new IFDSSolver(analysis)
    System.out.println("======================== IFDS Solver started  ========================")

    appendYamlReport("ifds_entrypoints_before_filtering_size", Scene.v().getEntryPoints.size())
    appendYamlReport("ifds_entrypoints_before_filtering", Scene.v().getEntryPoints.asScala.map(_.getSignature))

    val entrypoints = Scene.v().getEntryPoints.asScala.filter(m => {
      val c = m.getDeclaringClass
      appInfo.isActivity(c) || appInfo.isService(c) || appInfo.isReceiver(c)
    })

    val entrypointsFull = appInfo.allActivities.flatMap(controlFlowGraphManager.getRunner).map(_.method).toList
    appendYamlReport("entrypoints_full_size", entrypointsFull.size)
    appendYamlReport("entrypoints_full", entrypointsFull.map(_.getSignature))

    Scene.v().setEntryPoints((entrypoints ++ entrypointsFull).asJava)

    appendYamlReport("ifds_entrypoints_size", Scene.v().getEntryPoints.size())
    appendYamlReport("ifds_entrypoints", Scene.v().getEntryPoints.asScala.map(_.getSignature))

    ifdsSolver.solve()
    analyzedMethods.addAll(analysis.visitedMethods.asScala)
    System.out.println("======================== IFDS Solver finished ========================")
  }


  private def analyzeActivityPreVasco(activityClass: SootClass): Unit = {
    for ((handler, _) <- appInfo.getActivityHandlers(activityClass)) {
      controlFlowGraphManager.addActivityHandlerToEventLoop(activityClass, handler)
    }
  }


  def getIfdsResultAt(stmt: Stmt, target: Value): Iterable[AbstractValue] = {
    ifdsSolver.ifdsResultsAt(stmt).asScala.flatMap { case (tainted, taints) =>
      if (tainted.equivTo(target)) {
        taints
      } else {
        Set()
      }
    }
  }
}
