/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import com.research.nomad.markii.{Globals, Util}
import com.research.nomad.markii.dataflow.AbsNode.AnyNode
import presto.android.gui.listener.EventType
import presto.android.xml.{AndroidView, MethodInfo}
import soot.SootClass
import soot.jimple.Stmt

import scala.collection.mutable
import scala.jdk.CollectionConverters._

sealed abstract class AbsAttr extends Product with Serializable

object AbsAttr {
  final case class IntVal(i: Int) extends AbsAttr
  final case class StrVal(s: String) extends AbsAttr
  final case class ClassVal(c: SootClass) extends AbsAttr
}

/**
 * Node in Abstract Flow Tree
 */
sealed abstract class AbsNode extends Product with Serializable with AbsVal[AbsNode] {
  override def meet(other: AbsNode): AbsNode = AnyNode()
}

object AbsNode {
  /**
   * Node for a view element
   * @param allocSite: Allocation statement
   * @param id: Possible resource ids
   * @param sootClass: Associated class, e.g. android.widget.Button
   * @param attributes: Attribute values
   * @param androidView: Associated AndroidView from parsed XML
   */
  final case class ViewNode(allocSite: Stmt,
                            id: Set[Int] = Set(),
                            sootClass: Option[SootClass] = None,
                            attributes: Map[AndroidView.ViewAttr, Set[String]] = Map(),
                            buttonType: Option[DialogButtonType.Value] = None,
                            private val androidView: AndroidView = null) extends AbsNode {

    // We want this ID to be deterministic across runs..
    val nodeID: Int = {
      var hashCode = Globals.controlFlowGraphManager.stmtId(allocSite)
      for (i <- id) {
        hashCode ^= i
      }
      sootClass match {
        case Some(c) =>
          hashCode ^= c.getName.hashCode
        case None =>
      }
      for ((viewAttr, values) <- attributes) {
        hashCode ^= viewAttr.ordinal << 1
        for (v <- values) {
          hashCode ^= v.hashCode
        }
      }
      buttonType match {
        case Some(t) =>
          hashCode ^= t.id << 2
        case None =>
      }
      if (androidView != null) {
        hashCode ^= androidView.getId.toInt << 3
      }
      hashCode
    }

    def setAttributes(attrs: Set[(AndroidView.ViewAttr, String)]): ViewNode = {
      val newAttrs = mutable.Map[AndroidView.ViewAttr, Set[String]]()
      for ((attr, value) <- attrs) {
        newAttrs.put(attr, newAttrs.getOrElse(attr, Set()) + value)
      }
      for ((attr, values) <- attributes) {
        if (!newAttrs.contains(attr)) {
          newAttrs.put(attr, values)
        }
      }
      copy(attributes = newAttrs.toMap)
    }

    override def toString: String = {
      val attrStrings = mutable.ArrayBuffer[String]()
      if (id.nonEmpty) {
        attrStrings.addOne(f"id: [${id.mkString(",")}]")
      }
      if (sootClass.nonEmpty) {
        attrStrings.addOne(f"sootClass: ${sootClass.get}")
      }
      if (buttonType.nonEmpty) {
        attrStrings.addOne(f"buttonType: ${buttonType.get}")
      }
      attrStrings.addOne(f"attributes: ${attributes}" )
      f"ViewNode[${nodeID}](${attrStrings.mkString(",")})"
    }

    def getAttrs: Iterable[(AndroidView.ViewAttr, String)] = {
      val defaultAttrs = if (androidView != null) {
        androidView.getViewAttrs.asScala.filter { case (attr, _) => !attributes.contains(attr) }
      } else {
        List()
      }
      defaultAttrs ++ attributes.flatMap { case (attr, values) => values.map((attr, _)) }
    }

    def getAppAttrs: Iterable[(AndroidView.ViewAppAttr, String)] = if (androidView != null) {
      androidView.getViewAppAttrs.asScala
    } else {
      List()
    }

    def getInlineClickHandlers: Iterable[(EventType, MethodInfo)] = if (androidView != null) {
      androidView.getInlineClickHandlers.asScala
    } else {
      List()
    }
  }

  final case class AnyNode() extends AbsNode

  final case class ActNode(sootClass: SootClass) extends AbsNode

  final case class ListenerNode(listener: SootClass) extends AbsNode

  final case class LayoutParamsNode(attrs: Set[(AndroidView.ViewAttr, String)] = Set()) extends AbsNode

  final case class UnifiedObjectNode(absName: String, absAttrs: Map[String, AbsAttr]) extends AbsNode
}