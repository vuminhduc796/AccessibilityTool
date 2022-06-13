/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.analyses

import com.research.nomad.markii.{CallGraphManager, Constants, ControlFlowGraphManager, Core, Ic3Manager, PreAnalyses, Util}
import com.research.nomad.markii.dataflow.AbstractValue
import com.research.nomad.markii.instrument.{AllInstrument, DialogCreateInstrument}
import soot.{Local, RefType, Scene, SootClass, SootMethod}
import soot.jimple.{InstanceInvokeExpr, IntConstant, Jimple, Stmt}
import soot.jimple.toolkits.callgraph.Edge

import scala.collection.mutable
import scala.jdk.CollectionConverters._

class PreVASCO(core: Core, allInstrument: AllInstrument, dialogCreateInstrument: DialogCreateInstrument) {
  val showDialogInvocations = mutable.Map[Stmt, Local]()
  // NOTE: a type-safe way to prevent missing run All to configure heap transfer
  private val startWindowStmts: mutable.Set[Stmt] = mutable.Set()

  private var startActivityFacts = List[(SootMethod, SootMethod, SootClass)]()

  def getStartActivityFacts: Iterable[(SootMethod, SootMethod, SootClass)] = startActivityFacts
  def getShowDialogInvocations(stmt: Stmt): Option[Local] = showDialogInvocations.get(stmt)
  def isStartWindowStmt(stmt: Stmt): Boolean = startWindowStmts.contains(stmt)

  def analyze(handler: SootMethod): Unit = {
    val reachedMethods = core.callGraphManager.reachableMethods(handler)
    for (reached <- reachedMethods) {
      if (reached.getDeclaringClass.isApplicationClass && reached.isConcrete && reached.hasActiveBody) {
        val swaps = mutable.Map[Stmt, Stmt]()
        for (unit <- reached.getActiveBody.getUnits.asScala) {
          val stmt = unit.asInstanceOf[Stmt]
          if (stmt.containsInvokeExpr()) {
            val invokeExpr = stmt.getInvokeExpr
            val invokedMethod = Util.getMethodUnsafe(invokeExpr)
            if (invokedMethod != null) {
              if (invokedMethod.getSubSignature == "void startActivity(android.content.Intent)") {
                // NOTE: the base type is only used to provide an application context, thus it can't be used to infer the
                //       source activity
                core.getIfdsResultAt(stmt, invokeExpr.getArg(0)).foreach {
                  case AbstractValue.Intent(intent) =>
                    // FIXME: imprecision if we ignore the actions etc. fields?
                    val methods = mutable.Set[SootMethod]()
                    for (target <- intent.targets) {
                      core.controlFlowGraphManager.getRunner(target) match {
                        case Some(runner) => methods.add(runner.method)
                        case None =>
                      }
                      if (Ic3Manager.ic3Enabled) {
                        startActivityFacts :+= (handler, reached, target)
                      }
                    }
                    val base = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.getType.asInstanceOf[RefType].getSootClass
                    val runAllMethod = core.controlFlowGraphManager.getRunAll(stmt, methods, base, invokedMethod)
                    Scene.v().getCallGraph.removeAllEdgesOutOf(stmt)
                    Scene.v().getCallGraph.addEdge(new Edge(reached, stmt, runAllMethod))
                    // NOTE: no invocation/stmt swap
                    startWindowStmts.add(stmt)
                    invokeExpr.setMethodRef(runAllMethod.makeRef())
                  case _ =>
                }
              }

              // TODO: need to bind analyze listener setting in IFDS first
              // TODO: actually -- this is a more complicated recursive problem. but we can play it easy first.
              // FIXME: AlertDialog$Builder has a show method as well, this might not work well...but we take it as if it is a Dialog object now
              if (Constants.isDialogShow(invokedMethod.getSignature) ||
                Constants.isDialogBuilderShow(invokedMethod.getSignature)) {
                val dialogBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
                val methods = mutable.Set[SootMethod]()
                for (defStmt <- PreAnalyses.getDefsOfAt(reached, dialogBase, stmt)) {
                  core.controlFlowGraphManager.getRunnerOfDialog(defStmt) match {
                    case Some(runner) => methods.add(runner.method)
                    case None =>
                  }
                }
                if (methods.nonEmpty) {
                  // FIXME: I need to build a static class for this type of work
                  val runAllMethod = core.controlFlowGraphManager.getRunAllDialog(stmt, methods, reached)
                  val invocation = Jimple.v().newInvokeStmt(Jimple.v().newStaticInvokeExpr(runAllMethod.makeRef(), dialogBase))
                  Scene.v().getCallGraph.removeAllEdgesOutOf(stmt)
                  Scene.v().getCallGraph.addEdge(new Edge(reached, invocation, runAllMethod))
                  swaps.put(stmt, invocation)
                  startWindowStmts.add(invocation)
                  showDialogInvocations.put(invocation, dialogBase)
                }
              }
              if (invokedMethod.getSubSignature == "void showDialog(int)") {
                invokeExpr.getArg(0) match {
                  case intConstant: IntConstant =>
                    dialogCreateInstrument.getShowInvocationOfCreateDialog(reached, intConstant.value) match {
                      case Some(createMethod) =>
                        core.controlFlowGraphManager.getRunnerOfDialog(reached.getDeclaringClass, createMethod, intConstant) match {
                          case Some((runner, internalInvocation)) =>
                            val invocation = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(reached.getActiveBody.getThisLocal, runner.method.makeRef()))
                            core.callGraphManager.updateCall(reached, stmt, invocation, runner.method, Some(handler))
                            swaps.put(stmt, invocation)
                            startWindowStmts.add(invocation)
                            showDialogInvocations.put(internalInvocation, runner.view)
                          case None =>
                        }
                      case _ =>
                    }
                  case _ =>
                }
              }
              // Replace loadNativeAds with the load handler
              if (invokedMethod.getName == "loadNativeAds") {
                for ((argType, idx) <- invokedMethod.getParameterTypes.asScala.zipWithIndex) {
                  if (argType.toString == "com.applovin.nativeAds.AppLovinNativeAdLoadListener") {
                    val listenerArg = invokeExpr.getArg(idx).asInstanceOf[Local]
                    val listenerClass = listenerArg.getType.asInstanceOf[RefType].getSootClass
                    val adLoadHandler = listenerClass.getMethodByNameUnsafe("onNativeAdsLoaded")
                    if (adLoadHandler != null && core.appInfo.isActivity(reached.getDeclaringClass)) {
                      // Instrument adLoadHandler
                      allInstrument.instrumentRunOnUiThread(adLoadHandler)

                      // Replace invocation
                      val invocation = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(listenerArg, adLoadHandler.makeRef()))
                      core.callGraphManager.updateCall(reached, stmt, invocation, adLoadHandler, Some(handler))
                      swaps.put(stmt, invocation)
                    }
                  }
                }
              }
            }
          }
        }

        for ((out, in) <- swaps) {
          reached.getActiveBody.getUnits.swapWith(out, in)
        }
      }
    }
  }
}
