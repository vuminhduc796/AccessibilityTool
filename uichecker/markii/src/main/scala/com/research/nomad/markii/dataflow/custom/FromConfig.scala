/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow.custom

import java.io.FileReader

import com.research.nomad.markii.dataflow.{AbsVal, AbsValSet, CustomObjectStateTransformer, Ref}
import soot.{SootClass, SootMethod}
import soot.jimple.{InstanceInvokeExpr, Stmt}

import scala.collection.mutable
import scala.jdk.CollectionConverters._
import cats.syntax.either._
import io.circe._
import io.circe.generic.auto._
import io.circe.yaml

case class APISemanticConfig(baseClassName: String, states: List[String], initialState: String,
                             transferMap: Map[String, String])

case class AbsFS(state: Option[String] = None) extends AbsVal[AbsFS] {
  override def meet(other: AbsFS): AbsFS = {
    if (other.state == state) {
      this
    } else {
      AbsFS(None)
    }
  }
}

class FromConfig(configPath: String) extends CustomObjectStateTransformer[AbsValSet[AbsFS]] {

  private val json = yaml.parser.parse(new FileReader(configPath))

  private val api = json
    .leftMap(err => err: Error)
    .flatMap(_.as[APISemanticConfig])
    .valueOr(throw _)

  type D = AbsValSet[AbsFS]

  override def initInstance(sootClass: SootClass): Option[D] = {
    if (sootClass.getName == api.baseClassName) {
      Some(AbsValSet(Set(AbsFS(Some(api.initialState)))))
    } else {
      None
    }
  }

  /**
   * Key: Statement
   * Value: Set of possible transitions (ref-id, prev-state, post-state)
   */
  private val transitionSites = mutable.Map[Stmt, mutable.Set[(Option[Ref], AbsFS, String)]]()

  def getTransitions(m: SootMethod): Set[(Option[Ref], AbsFS, String)] = {
    m.getActiveBody.getUnits.asScala.flatMap(u => transitionSites.getOrElse(u.asInstanceOf[Stmt], Set())).toSet
  }

  override def updatedInstance(prevVals: D, instanceInvokeExpr: InstanceInvokeExpr, callSite: Stmt, ref: Option[Ref]): D = {
    api.transferMap.get(instanceInvokeExpr.getMethod.getSignature) match {
      case Some(nextState) =>
        for (prevVal <- prevVals.vals) {
          transitionSites.getOrElseUpdate(callSite, mutable.Set()).add((ref, prevVal, nextState))
        }
        AbsValSet(Set(AbsFS(Some(nextState))))
      case None => prevVals
    }
  }
}
