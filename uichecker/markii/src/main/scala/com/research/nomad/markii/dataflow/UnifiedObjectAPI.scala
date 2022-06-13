/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import com.research.nomad.markii.Globals
import com.research.nomad.markii.dataflow.AbsNode.UnifiedObjectNode
import soot.{RefType, Scene, SootClass}
import soot.jimple.{ClassConstant, InstanceInvokeExpr}

object UnifiedObjectAPI {
  private val absNames = Map(
    "androidx.work.WorkRequest$Builder" -> "WorkRequest"
  )

  def isBaseClass(sootClass: SootClass): Boolean = {
    getAbsName(sootClass).nonEmpty
  }

  def getAbsName(sootClass: SootClass): Option[String] = {
    for ((baseClassName, absName) <- absNames) {
      val baseClass = Scene.v.getSootClass(baseClassName)
      if (Globals.appInfo.hier.isSubclassOf(sootClass, baseClass)) {
        return Some(absName)
      }
    }
    None
  }

  def newFrom(sootClass: SootClass): AbsNode = {
    UnifiedObjectNode(getAbsName(sootClass).get, Map())
  }

  def invokeFrom(absName: String, attrs: Map[String, AbsAttr],
                 instanceInvokeExpr: InstanceInvokeExpr): Option[Map[String, AbsAttr]] = {
    val invokedMethod = instanceInvokeExpr.getMethod
    val baseClass = invokedMethod.getDeclaringClass
    getAbsName(baseClass) match {
      case Some(n) if n == absName =>
        if (invokedMethod.getSignature == "<androidx.work.PeriodicWorkRequest$Builder: void <init>(java.lang.Class,long,java.util.concurrent.TimeUnit)>") {
          instanceInvokeExpr.getArg(0) match {
            case classConstant: ClassConstant =>
              classConstant.toSootType match {
                case refType: RefType =>
                  val sootClass = refType.getSootClass
                  return Some(Map("workerClass" -> AbsAttr.ClassVal(sootClass)))
                case _ =>
              }
            case _ =>
          }
        }
        None
      case None => None
    }
  }
}
