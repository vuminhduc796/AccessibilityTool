/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.instrument

import com.research.nomad.markii.Core
import soot.{Body, SootClass, SootMethod}
import soot.jimple.{EqExpr, IfStmt, IntConstant, JimpleBody, LookupSwitchStmt, Stmt}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

class DialogCreateInstrument(core: Core) {
  private val showCreateDialog = mutable.Map[SootClass, mutable.Map[Int, SootMethod]]()

  private def getIfTarget(method: SootMethod, i: Int): Stmt = {
    val paramLocal = method.getActiveBody.getParameterLocal(0)
    for (unit <- method.getActiveBody.getUnits.asScala) {
      unit match {
        case ifStmt: IfStmt =>
          ifStmt.getCondition match {
            case eqExpr: EqExpr =>
              if (eqExpr.getOp1.equivTo(paramLocal) && eqExpr.getOp2.asInstanceOf[IntConstant].value == i) {
                return ifStmt.getTarget
              }
          }
        case _ =>
      }
    }
    null
  }


  private def copyMethod(method: SootMethod, suffix: String): SootMethod = {
    val newMethod = new SootMethod(method.getName + suffix, method.getParameterTypes, method.getReturnType, method.getModifiers)
    val newBody = method.getActiveBody.asInstanceOf[JimpleBody].clone().asInstanceOf[Body]
    newMethod.setActiveBody(newBody)
    newMethod
  }

  private def pruneFirstLookupSwitchExcept(method: SootMethod, i: Int): Unit = {
    val paramLocal = method.getActiveBody.getParameterLocal(0)
    for (unit <- method.getActiveBody.getUnits.asScala) {
      unit match {
        case lookupSwitchStmt: LookupSwitchStmt =>
          assert(lookupSwitchStmt.getKey.equivTo(paramLocal))
          for ((value, idx) <- lookupSwitchStmt.getLookupValues.asScala.zipWithIndex) {
            if (value.value != i) {
              lookupSwitchStmt.setTarget(idx, lookupSwitchStmt.getDefaultTarget)
            }
          }
          return
        case _ =>
      }
    }
    throw new Exception("No lookup")
  }

  private def pruneIfExcept(method: SootMethod, i: Int): Unit = {
    val paramLocal = method.getActiveBody.getParameterLocal(0)
    val iTarget = getIfTarget(method, i)
    assert(iTarget != null)
    for (unit <- method.getActiveBody.getUnits.asScala) {
      unit match {
        case ifStmt: IfStmt =>
          ifStmt.getCondition match {
            case eqExpr: EqExpr =>
              if (eqExpr.getOp1.equivTo(paramLocal) && eqExpr.getOp2.asInstanceOf[IntConstant].value != i) {
                ifStmt.setTarget(iTarget)
              }
          }
        case _ =>
      }
    }
  }
  def run(allActivities: Iterable[SootClass]): Unit = {
    for (activity <- allActivities) {
      // FIXME: use related filter method in Constants
      val method = activity.getMethodUnsafe("android.app.Dialog onCreateDialog(int)")
      if (method != null) {
        run_(method, activity)
      }
    }
  }

  private def run_(method: SootMethod, activity: SootClass): Unit = {
    val paramLocal = method.getActiveBody.getParameterLocal(0)
    var hasIfStmt = false
    var hasSuperOnCreateDialog = false
    // FIXME: this structure is not working well -- esp. when the onCreateDialog is just a wrapper of some other
    //        invocation
    for (unit <- method.getActiveBody.getUnits.asScala) {
      unit match {
        case lookupSwitchStmt: LookupSwitchStmt =>
          assert(lookupSwitchStmt.getKey.equivTo(paramLocal))
          for (value <- lookupSwitchStmt.getLookupValues.asScala) {
            val newMethod = copyMethod(method, "_" + value.value)
            pruneFirstLookupSwitchExcept(newMethod, value.value)
            activity.addMethod(newMethod)
            showCreateDialog.getOrElseUpdate(activity, mutable.Map()).put(value.value, newMethod)
            core.controlFlowGraphManager.addToMethodMap(newMethod)
          }
          return
        case ifStmt: IfStmt =>
          ifStmt.getCondition match {
            case eqExpr: EqExpr =>
              if (eqExpr.getOp1.equivTo(paramLocal)) {
                hasIfStmt = true
                val i = eqExpr.getOp2.asInstanceOf[IntConstant].value
                val newMethod = copyMethod(method, "_" + i)
                pruneIfExcept(newMethod, i)
                activity.addMethod(newMethod)
                showCreateDialog.getOrElseUpdate(activity, mutable.Map()).put(i, newMethod)
                core.controlFlowGraphManager.addToMethodMap(newMethod)
              }
            case _ =>
          }
        case stmt: Stmt =>
          if (stmt.containsInvokeExpr() && stmt.getInvokeExpr.getMethod.getName == "onCreateDialog") {
            hasSuperOnCreateDialog = true
          }
      }
    }
  }

  def getShowInvocationOfCreateDialog(reached: SootMethod, createDialogId: Int): Option[SootMethod] = {
    showCreateDialog.get(reached.getDeclaringClass) match {
      case Some(m) => m.get(createDialogId)
      case None => None
    }
  }
}
