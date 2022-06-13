/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.instrument

import com.research.nomad.markii.{AppInfo, Constants, Core, Util}
import presto.android.MethodNames
import soot.{Local, RefType, Scene, SootMethod}
import soot.jimple.{InstanceInvokeExpr, Jimple, NullConstant, Stmt}
import soot.jimple.toolkits.callgraph.Edge

import scala.jdk.CollectionConverters._

class DialogInitInstrument(core: Core) {
  def run(): Unit = {
    for (c <- Scene.v.getApplicationClasses.asScala) {
      val methods = c.getMethods.asScala.toList
      for (m <- methods) {
        if (m.isConcrete && m.hasActiveBody) {
          val customDialogInit: Iterable[(soot.Unit, Local, SootMethod)] = m.getActiveBody.getUnits.asScala.flatMap {
            case stmt: Stmt if stmt.containsInvokeExpr() =>
              val invoked = Util.getMethodUnsafe(stmt.getInvokeExpr)
              if (invoked != null) {
                stmt.getInvokeExpr match {
                  case instanceInvokeExpr: InstanceInvokeExpr if invoked.getName == "<init>" =>
                    val baseClass = instanceInvokeExpr.getBase.getType.asInstanceOf[RefType].getSootClass
                    if (baseClass.isConcrete) {
                      val onCreate = core.appInfo.hier.virtualDispatch(MethodNames.onDialogCreateSubSig, baseClass)
                      if (core.appInfo.isDialogClass(baseClass) && onCreate != null && onCreate.isConcrete && onCreate.hasActiveBody) {
                        Some((stmt, instanceInvokeExpr.getBase.asInstanceOf[Local], onCreate))
                      } else {
                        None
                      }
                    } else {
                      None
                    }
                  case _ => None
                }
              } else {
                None
              }
            case _ => None
          }
          for ((stmt, base, onCreate) <- customDialogInit) {
            val invocation = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(base, onCreate.makeRef(), NullConstant.v()))
            Scene.v().getCallGraph.addEdge(new Edge(m, invocation, onCreate))
            m.getActiveBody.getUnits.insertAfter(invocation, stmt)
          }
        }
      }
    }
  }
}
