/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii

import soot.{Local, SootMethod}
import soot.jimple.Stmt
import soot.jimple.toolkits.pointer.LocalMustAliasAnalysis
import soot.toolkits.graph.CompleteUnitGraph
import soot.toolkits.scalar.{SimpleLiveLocals, SmartLocalDefs}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

object PreAnalyses {
  private val aliasAnalysisMap = mutable.Map[SootMethod, LocalMustAliasAnalysis]()
  private val localDefsMap = mutable.Map[SootMethod, SmartLocalDefs]()

  def getLocalDefs(m: SootMethod) : SmartLocalDefs = {
    if (!localDefsMap.contains(m)) {
      val ug = new CompleteUnitGraph(m.getActiveBody)
      localDefsMap.addOne(m, new SmartLocalDefs(ug, new SimpleLiveLocals(ug)))
    }
    localDefsMap(m)
  }

  def getDefsOfAt(m: SootMethod, l: Local, u: soot.Unit): Set[Stmt] = {
    getLocalDefs(m).getDefsOfAt(l, u).asScala.toSet.map((u: soot.Unit) => u.asInstanceOf[Stmt])
  }

  def isAlias(l1: Local, l2: Local, stmt1: Stmt, stmt2: Stmt, m: SootMethod): Boolean = {
    if (l1.equivTo(l2)) {
      return true
    }
    if (!aliasAnalysisMap.contains(m)) {
      val ug = new CompleteUnitGraph(m.getActiveBody)
      aliasAnalysisMap.addOne(m, new LocalMustAliasAnalysis(ug, false))
    }
    val analysis = aliasAnalysisMap(m)
    analysis.mustAlias(l1, stmt1, l2, stmt2) || getLocalDefs(m).getDefsOf(l2) == getLocalDefs(m).getDefsOf(l1)
  }

}
