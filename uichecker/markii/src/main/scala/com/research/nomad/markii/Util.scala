/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii

import java.io.{BufferedWriter, FileWriter}

import soot.{SootMethod, UnitPatchingChain}
import soot.jimple.{InvokeExpr, Stmt}
import vasco.DataFlowSolution

import scala.collection.mutable
import scala.jdk.CollectionConverters._
import io.github.izgzhen.msbase.JsonUtil

object Util {
  /**
   * getMethod will throw exception sometimes...
   *
   * @param invokeExpr
   * @return
   */
  def getMethodUnsafe(invokeExpr: InvokeExpr): SootMethod = {
    try {
      invokeExpr.getMethod
    } catch {
      case ignored: Exception =>
        null
    }
  }

  def getMethodByNameUnsafe(clazz: soot.SootClass, name: String): Option[SootMethod] = {
    try {
      clazz.getMethodByNameUnsafe(name) match {
        case null => None
        case m => Some(m)
      }
    } catch {
      case ignored: Exception =>
        None
    }
  }

  def locateStmt(sootMethod: SootMethod, stmt: Stmt): String = {
    val lines = mutable.ArrayBuffer[String]()

    for (unit <- sootMethod.getActiveBody.getUnits.asScala) {
      if (unit != stmt) {
        lines.addOne(unit.toString)
      } else {
        lines.addOne("************************")
        lines.addOne(unit.toString)
        lines.addOne("************************")
      }
    }
    lines.mkString("\n")
  }

  def getUnitIndex(units: UnitPatchingChain, u: soot.Unit): Int = {
    units.asScala.view.toSeq.indexOf(u)
  }

  def dumpVASCOAbstractions[D](outputPath: String, solution: DataFlowSolution[soot.Unit, D],
                               nonEmpty: D => Boolean,
                               domainToJSONObj: D => Object,
                               methods: Iterable[SootMethod]): Unit = {
    val outputData = mutable.Map[String, Object]()
    for (m <- methods) {
      val methodData = mutable.ArrayBuffer[(String, Object)]()
      if (m.hasActiveBody) { // To fix CI error https://github.com/izgzhen/markii/pull/75/checks?check_run_id=1647042974
        for (unit <- m.getActiveBody.getUnits.asScala) {
          val d = solution.getValueAfter(unit)
          if (d != null && nonEmpty(d)) {
            methodData.addOne((unit.toString, domainToJSONObj(d)))
          }
        }
        outputData.put(m.getSignature, Map(
          "body" -> m.getActiveBody.toString,
          "abstractions" -> methodData.toList
        ))
      }
    }
    val bw = new BufferedWriter(new FileWriter(outputPath))
    bw.write(JsonUtil.toJson(outputData))
    bw.close()
  }

  def getJavaLineNumber(sootMethod : SootMethod): Int = {
    if (!sootMethod.hasActiveBody || sootMethod.getActiveBody == null) {
      return -1
    }
    for (unit <- sootMethod.getActiveBody.getUnits.asScala) {
      val tmp = unit.getJavaSourceStartLineNumber
      if (tmp != -1){
        return tmp
      }
    }
    -1
  }
}
