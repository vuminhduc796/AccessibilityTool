/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.instrument

import com.research.nomad.markii.dataflow.Ref
import com.research.nomad.markii.{AppInfo, CallGraphManager, Constants, ControlFlowGraphManager, Core}
import soot.{Local, RefType, SootClass, SootMethod}
import soot.jimple.{InstanceInvokeExpr, Jimple, Stmt}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

class AllInstrument(core: Core) {
  def instrumentRunOnUiThread(m: SootMethod): Unit = {
    val swaps = mutable.Map[Stmt, Stmt]()
    for (unit <- m.getActiveBody.getUnits.asScala) {
      val stmt = unit.asInstanceOf[Stmt]
      if (stmt.containsInvokeExpr()) {
        val invokeExpr = stmt.getInvokeExpr
        if (core.appInfo.isActivityRunOnUiThread(invokeExpr.getMethod)) {
          val runnableArg = invokeExpr.getArg(0).asInstanceOf[Local]
          val runnableArgClass = runnableArg.getType.asInstanceOf[RefType].getSootClass
          val runMethod = runnableArgClass.getMethodByNameUnsafe("run")
          val invocation = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(runnableArg, runMethod.makeRef()))
          core.callGraphManager.updateCall(m, stmt, invocation, runMethod)
          swaps.put(stmt, invocation)
        }
      }
    }
    for ((out, in) <- swaps) {
      m.getActiveBody.getUnits.swapWith(out, in)
    }
  }

  /**
   * @param m
   */
  private def instrumentMethod(m: SootMethod): Unit = {
    val swaps = mutable.Map[Stmt, Stmt]()
    for (unit <- m.getActiveBody.getUnits.asScala) {
      val stmt = unit.asInstanceOf[Stmt]
      if (stmt.containsInvokeExpr()) {
        val invokeExpr = stmt.getInvokeExpr
        if (invokeExpr.getMethod.getSignature == "<android.os.CountDownTimer: android.os.CountDownTimer start()>") {
          // Example: a8e458e619d5235fe8a97ea0186961acc1192ed13bb28a79b493c752747cc683
          val timer = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
          val timerClass = timer.getType.asInstanceOf[RefType].getSootClass
          val onFinish = timerClass.getMethodByNameUnsafe("onFinish")
          val invocation = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(timer, onFinish.makeRef()))
          core.callGraphManager.updateCall(m, stmt, invocation, onFinish)
          swaps.put(stmt, invocation)
        } else if (core.appInfo.hier.isSubclassOf(invokeExpr.getMethod.getDeclaringClass, Constants.dialogFragmentClass)) {
          if (invokeExpr.getMethod.getSubSignature == "void <init>()") {
            val instanceInvokeExpr = invokeExpr.asInstanceOf[InstanceInvokeExpr]
            val baseLocal = instanceInvokeExpr.getBase
            val baseClass = baseLocal.getType.asInstanceOf[RefType].getSootClass
            core.controlFlowGraphManager.getRunnerofDialogFragment(baseClass) match {
              case Some(runner) =>
                val invocation = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(baseLocal.asInstanceOf[Local], runner.makeRef()))
                core.callGraphManager.updateCall(m, stmt, invocation, runner.method)
                swaps.put(stmt, invocation)
            }
          }
        }
      }
    }
    for ((out, in) <- swaps) {
      m.getActiveBody.getUnits.swapWith(out, in)
    }
  }

  def run(allActivities: Iterable[SootClass]): Unit = {
    for (activity <- allActivities) {
      for (method <- activity.getMethods.asScala) {
        if (method.isConcrete && method.hasActiveBody) {
          // FIXME: remove the mainActivity workaround by fixing this
          instrumentMethod(method)
        }
      }
    }
  }
}
