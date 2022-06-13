/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii

import presto.android.Configs
import soot.{RefType, Scene, SootMethod}
import soot.jimple.{InstanceInvokeExpr, Stmt}
import soot.jimple.toolkits.callgraph.Edge

import scala.collection.mutable
import scala.jdk.CollectionConverters._

/**
 * Make CallGraph Great Again!
 *
 * This (should) wraps over any call-graph related API in soot.
 */
class CallGraphManager(appInfo: AppInfo) {
  // Constructor:
  private val extraEdgeOutMap: mutable.Map[SootMethod, mutable.Set[SootMethod]] = mutable.Map()
  private val methodAndReachables = mutable.Map[SootMethod, mutable.Set[SootMethod]]()
  patchCallGraph()
  private val methodTargets: Map[SootMethod, Set[SootMethod]] = Scene.v().getCallGraph.sourceMethods().asScala.map(src => (src.method(), Scene.v().getCallGraph.edgesOutOf(src).asScala.map(_.getTgt.method()).toSet)).toMap

  def reachableMethods(m: SootMethod): Set[SootMethod] = {
    _reachableMethods(m).union(Set(m))
  }

  def updateCall(src: SootMethod, oldStmt: Stmt, newStmt: Stmt,
                 target: SootMethod, srcContext: Option[SootMethod] = None): Unit = {
    Scene.v().getCallGraph.removeAllEdgesOutOf(oldStmt)
    Scene.v().getCallGraph.addEdge(new Edge(src, newStmt, target))
    methodAndReachables.getOrElseUpdate(src, mutable.Set()).add(target)
    srcContext match {
      case Some(contextMethod) =>
        methodAndReachables.getOrElseUpdate(contextMethod, mutable.Set()).add(target)
      case None =>
    }
  }

  private def isTargetMethod(target: SootMethod): Boolean =
    target.isConcrete && target.hasActiveBody && target.getDeclaringClass.isApplicationClass &&
      (!Configs.isLibraryClass(target.getDeclaringClass.getName))

  private def patchCallGraph(): Unit = {
    for (c <- Scene.v().getApplicationClasses.asScala) {
      for (m <- c.getMethods.asScala) {
        if (m.isConcrete && m.hasActiveBody) {
          for (unit <- m.getActiveBody.getUnits.asScala) {
            val stmt = unit.asInstanceOf[Stmt]
            if (stmt.containsInvokeExpr()) {
              val dispatchedTargets = mutable.Set[SootMethod]()
              val invokedTarget = Util.getMethodUnsafe(stmt.getInvokeExpr)
              if (invokedTarget != null) {
                if (isTargetMethod(invokedTarget)) {
                  dispatchedTargets.add(invokedTarget)
                } else {
                  stmt.getInvokeExpr match {
                    case instanceInvokeExpr: InstanceInvokeExpr =>
                      instanceInvokeExpr.getBase.getType match {
                        case refType: RefType if refType.getSootClass.isConcrete =>
                          val dispatchedTarget = appInfo.hier.virtualDispatch(invokedTarget, refType.getSootClass)
                          if (dispatchedTarget != null && isTargetMethod(dispatchedTarget)) {
                            dispatchedTargets.add(dispatchedTarget)
                          } else {
                            val subTypes = appInfo.hier.getConcreteSubtypes(refType.getSootClass).asScala
                            if (subTypes.size < 5) { // FIXME: avoid over-explosion....
                              for (subClass <- subTypes) {
                                if (subClass != null && subClass.isConcrete) {
                                  val dispatchedTarget = appInfo.hier.virtualDispatch(invokedTarget, subClass)
                                  if (dispatchedTarget != null) {
                                    dispatchedTargets.add(dispatchedTarget)
                                  }
                                }
                              }
                            }
                          }
                        case _ =>
                      }
                    case _ =>
                  }
                }
              }
              for (target <- dispatchedTargets) {
                if (isTargetMethod(target)) {
                  var edge: Edge = null
                  try {
                    edge = Scene.v().getCallGraph.findEdge(stmt, target)
                  } catch {
                    case ignored: Exception =>
                  }
                  if (edge == null) {
                    Scene.v().getCallGraph.addEdge(new Edge(m, stmt, target))
                  }
                }
                if (target.getSignature == "<android.os.Handler: boolean postDelayed(java.lang.Runnable,long)>") {
                  val runnableType = stmt.getInvokeExpr.getArg(0).getType.asInstanceOf[RefType]
                  if (runnableType.getSootClass.isConcrete) {
                    val run = appInfo.hier.virtualDispatch(Scene.v().getMethod("<java.lang.Runnable: void run()>"), runnableType.getSootClass)
                    if (run != null) {
                      extraEdgeOutMap.getOrElseUpdate(m, mutable.Set()).add(run)
                    } else {
                      println("No run in " + runnableType.getSootClass)
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  private def _reachableMethods(m: SootMethod): Set[SootMethod] = {
    methodAndReachables.get(m) match {
      case Some(s) => return s.toSet
      case None =>
    }
    val reachables = mutable.Set[SootMethod](m)
    methodAndReachables.put(m, reachables)
    val worklist = mutable.Queue[SootMethod]()
    worklist.addOne(m)
    while (worklist.nonEmpty) {
      val source = worklist.dequeue()
      methodTargets.get(source) match {
        case Some(targets) =>
          for (target <- targets) {
            if (!reachables.contains(target)) {
              reachables.add(target)
              worklist.addOne(target)
            }
          }
        case None =>
      }
      // FIXME: refactor duplicated code
      extraEdgeOutMap.get(source) match {
        case Some(targets) =>
          for (target <- targets) {
            if (!reachables.contains(target)) {
              reachables.add(target)
              worklist.addOne(target)
            }
          }
        case None =>
      }
    }
    reachables.toSet
  }
}
