package com.research.nomad.markii.analyses

import com.research.nomad.markii.Core
import com.research.nomad.markii.dataflow.{AFTDomain, AbstractValuePropVASCO}
import soot.SootMethod
import soot.toolkits.graph.DirectedGraph
import vasco.{DataFlowSolution, ProgramRepresentation}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

case class FlowInsensitiveAnalysisMixin(core: Core, preVasco: PreVASCO, entryPoints: List[SootMethod],
                                           analysis: FlowInsensitiveAnalysis)
  extends AbstractValuePropVASCO(core, preVasco, entryPoints) {

  override def onNewCall(method: SootMethod, invocation: soot.Unit): Unit = analysis.onNewCall(method, invocation)
}

abstract class FlowInsensitiveAnalysisImpl[M, N, A] extends InterProcDataAnalysis[M, N, A]{
  implicit val ord: Ordering[WorkListItemM[M, N]] = new Ordering[WorkListItemM[M, N]] {
    override def compare(x: WorkListItemM[M, N], y: WorkListItemM[M, N]): Int = {
      x.method.hashCode() - y.method.hashCode()
    }
  }

  protected val workList = mutable.TreeSet[WorkListItemM[M, N]]()
  private val values: mutable.Map[M, A] = mutable.Map()
  private val callers: mutable.Map[M, mutable.Set[(M, DirectedGraph[N])]] = mutable.Map()

  def onNewCall(method: M, invocation: N): Unit = {
    workList.addOne(WorkListItemM(method, programRepresentation.getControlFlowGraph(method)))
  }

  private def units(m: M): Iterable[N] = {
    programRepresentation.getControlFlowGraph(m).iterator().asScala.toList
  }

  def getMeetOverValidPathsSolution: DataFlowSolution[N, A] = {
    val unitValues = values.flatMap { case (m, a) => units(m).map(u => (u, a)) }.asJava
    new DataFlowSolution[N, A](unitValues, unitValues)
  }

  def getMethods: Iterable[M] = values.keys

  def doAnalysis(): Unit = {
    for (method <- programRepresentation.getEntryPoints.asScala) {
      initMethodEntryValue(method, boundaryValue(method))
    }

    while (workList.nonEmpty) {
      val item = workList.last
      workList.remove(item)

      val in = values.getOrElse(item.method, topValue)

      var out = topValue
      val contextMethod = item.method

      for (node <- item.cfg.asScala) {
        if (programRepresentation.isCall(node)) {
          var hit = false
          for (targetMethod <- programRepresentation.resolveTargets(contextMethod, node).asScala) {
            val entryValue = callEntryFlowFunction(targetMethod, targetMethod, node, in)
            callers.getOrElseUpdate(targetMethod, mutable.Set()).addOne((contextMethod, item.cfg))

            val v = values.get(targetMethod) match {
              case Some(v) => {
                if (v != meet(v, entryValue)) {
                  values.put(targetMethod, meet(v, entryValue))
                  workList.addOne(WorkListItemM(targetMethod, programRepresentation.getControlFlowGraph(targetMethod)))
                }
                meet(v, entryValue)
              }
              case None => {
                val v = initMethodEntryValue(targetMethod, entryValue)
                values.put(targetMethod, v)
                v
              }
            }

            hit = true
            out = meet(out, callExitFlowFunction(contextMethod, targetMethod, node, v))
          }
          if (!hit) {
            out = meet(out, callLocalFlowFunction(contextMethod, node, in))
          }
        } else {
          out = meet(out, normalFlowFunction(contextMethod, node, in))
        }
      }

      // Merge with previous OUT to force monotonicity (harmless if flow functions are monotinic)
      out = meet(out, in)

      values.put(item.method, out)

      // If OUT has changed...
      if (!(out == in)) { // Then add successors to the work-list.
        workList.addOne(WorkListItemM(contextMethod, item.cfg))
        for (caller <- callers.getOrElse(item.method, Set())) {
          workList.addOne(WorkListItemM(caller._1, caller._2))
        }
      }
    }
  }

  def initMethodEntryValue(method: M, entryValue: A): A
}

case class FlowInsensitiveAnalysis(core: Core, preVasco: PreVASCO, entryPoints: List[SootMethod])
  extends FlowInsensitiveAnalysisImpl[SootMethod, soot.Unit, AFTDomain] {
  val mixin = FlowInsensitiveAnalysisMixin(core, preVasco, entryPoints, this)

  override def initMethodEntryValue(method: SootMethod, entryValue: AFTDomain): AFTDomain = {
    val cfg = programRepresentation.getControlFlowGraph(method)
    workList.addOne(WorkListItemM(method, cfg))
    entryValue
  }

  override def normalFlowFunction(contextMethod: SootMethod, node: soot.Unit, inValue: AFTDomain): AFTDomain =
    mixin.normalFlowFunction(contextMethod, node, inValue)

  override def callEntryFlowFunction(contextMethod: SootMethod, targetMethod: SootMethod, node: soot.Unit, inValue: AFTDomain): AFTDomain =
    mixin.callEntryFlowFunction(contextMethod, targetMethod, node, inValue)

  override def callExitFlowFunction(contextMethod: SootMethod, targetMethod: SootMethod, node: soot.Unit, exitValue: AFTDomain): AFTDomain =
    mixin.callExitFlowFunction(contextMethod, targetMethod, node, exitValue)

  override def callLocalFlowFunction(contextMethod: SootMethod, node: soot.Unit, inValue: AFTDomain): AFTDomain =
    mixin.callLocalFlowFunction(contextMethod, node, inValue)

  override def programRepresentation: ProgramRepresentation[SootMethod, soot.Unit] =
    mixin.programRepresentation()

  override def topValue: AFTDomain = mixin.topValue()

  override def meet(op1: AFTDomain, op2: AFTDomain): AFTDomain = mixin.meet(op1, op2)

  override def boundaryValue(entryPoint: SootMethod): AFTDomain = mixin.boundaryValue(entryPoint)

  override def copy(src: AFTDomain): AFTDomain = mixin.copy(src)
}