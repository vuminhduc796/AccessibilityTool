/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import com.research.nomad.markii.Util.getJavaLineNumber
import com.research.nomad.markii.{AppInfo, Constants, Globals, PreAnalyses}
import com.research.nomad.markii.dataflow.AbsNode.{ActNode, LayoutParamsNode, ListenerNode, UnifiedObjectNode, ViewNode}
import presto.android.gui.listener.EventType
import presto.android.xml.AndroidView
import soot.jimple.{InstanceInvokeExpr, IntConstant, Stmt, StringConstant}
import soot.{Local, SootClass, SootMethod, Value}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

object DialogButtonType extends Enumeration {
  type DialogButtonType = Value
  val POSITIVE, NEGATIVE, NEUTRAL = Value
}

case class AbsValSet[D <: AbsVal[D]](vals: Set[D] = Set(), merged: Option[D] = None) extends AbsVal[AbsValSet[D]] {
  override def meet(other: AbsValSet[D]): AbsValSet[D] = {
    val allValues = vals ++ other.vals
    if (allValues.size > 100) {
      val merged: D = allValues.reduce((v1, v2) => v1.meet(v2))
      return AbsValSet(vals=Set(), merged=Some(merged))
    }
    AbsValSet[D](allValues)
  }

  def map(f: D => D): AbsValSet[D] = AbsValSet[D](vals.map(f))
}

trait Traverser {
  def withSubNode(d: AFTDomain, viewNode: ViewNode): AFTDomain
}

case class SourceLoc(file: String, lineNumber: Int)

object SourceLoc {
  def fromJavaLinked(handler: SootMethod): SourceLoc =
    SourceLoc("method linked in java", getJavaLineNumber(handler))
}

/**
 * Data domain of Abstract Flow Tree
 * NOTE: UPDATE STRUCTURAL METHODS when the data structure is changed
 */
case class AFTDomain(private val localNodeMap: Map[Local, AccessPath[AbsValSet[AbsNode]]], // FIXME: consider aliasing carefully when writing to localNodeMap
                     private val globalNodeMap: Map[SootClass, AccessPath[AbsValSet[AbsNode]]],
                     currentWindowClasses: Set[SootClass], // The set of possible current activity/dialog class for the current statement
                     nodeEdgeMap: Map[ViewNode, Set[ViewNode]],
                     nodeEdgeRevMap: Map[ViewNode, Set[ViewNode]],
                     nodeHandlerMap: Map[(ViewNode, EventType), Set[(SootMethod, SourceLoc)]], // SourceLoc is the loc of definition
                     dialogHandlerMap: Map[(ViewNode, DialogButtonType.Value), Set[SootMethod]],
                     activityRootViewMap: Map[SootClass, Set[ViewNode]]) {

  /**
   * STRUCTURAL METHOD
   */
  def meet(d: AFTDomain): AFTDomain = {
    if (equals(AFTDomain.top)) return d
    if (d.equals(AFTDomain.top)) return this
    if (equals(d)) return this
    AFTDomain(
      AFTDomain.mergeMapOfAccessPath(localNodeMap, d.localNodeMap),
      AFTDomain.mergeMapOfAccessPath(globalNodeMap, d.globalNodeMap),
      currentWindowClasses.union(d.currentWindowClasses),
      AFTDomain.mergeMapOfSets(nodeEdgeMap, d.nodeEdgeMap),
      AFTDomain.mergeMapOfSets(nodeEdgeRevMap, d.nodeEdgeRevMap),
      AFTDomain.mergeMapOfSets(nodeHandlerMap, d.nodeHandlerMap),
      AFTDomain.mergeMapOfSets(dialogHandlerMap, d.dialogHandlerMap),
      AFTDomain.mergeMapOfSets(activityRootViewMap, d.activityRootViewMap))
  }

  /**
   * STRUCTURAL METHOD
   * NOTE: If you are trying to mutate view nodes (e.g. its attributes), use updateLocalViewNodes instead.
   *
   * nodeToNode: Mutator which process any node that is not view node.
   */
  private def updateLocalNonViewNodes(contextMethod: SootMethod, stmt: Stmt, local: Local,
                                      nodeToNode: AbsNode => AbsNode): AFTDomain = {
    copy(localNodeMap = localNodeMap.map { case (l, accessPath) =>
      if (PreAnalyses.isAlias(local, l, stmt, stmt, contextMethod)) {
        (l, accessPath.updateData((x, _) => x.map {
          case viewNode: ViewNode => viewNode
          case nonViewNode => nodeToNode(nonViewNode)
        }, None))
      } else {
        (l, accessPath)
      }
    })
  }

  /**
   * STRUCTURAL METHOD
   */
  private def updateLocalViewNodes(contextMethod: SootMethod, stmt: Stmt, local: Local,
                                   nodeToNode: ViewNode => ViewNode): AFTDomain = {
    val selectedViewNodeIDs = mutable.Set[Integer]()
    localNodeMap.foreach { case (l, accessPath) =>
      if (PreAnalyses.isAlias(local, l, stmt, stmt, contextMethod)) {
        if (accessPath.data.nonEmpty) {
          for (absNode <- accessPath.data.get.vals) {
            absNode match {
              case viewNode: ViewNode => selectedViewNodeIDs.add(viewNode.nodeID)
              case _ =>
            }
          }
        }
      }
    }
    updateAllViewNodes(viewNode => if (selectedViewNodeIDs.contains(viewNode.nodeID)) {
      nodeToNode(viewNode)
    } else {
      viewNode
    })
  }

  /**
   * STRUCTURAL METHOD
   */
  private def updateAllViewNodes(nodeToNode: ViewNode => ViewNode): AFTDomain = {
    AFTDomain(
      localNodeMap = localNodeMap.view.mapValues(_.updateData((x, _) => x.map {
        case v: ViewNode => nodeToNode(v)
        case n => n
      }, None)).toMap,
      globalNodeMap = globalNodeMap.view.mapValues(_.updateData((x, _) => x.map {
        case v: ViewNode => nodeToNode(v)
        case n => n
      }, None)).toMap,
      currentWindowClasses = currentWindowClasses,
      nodeEdgeMap = nodeEdgeMap.map { case (key, values) => (nodeToNode(key), values.map(nodeToNode)) },
      nodeEdgeRevMap = nodeEdgeRevMap.map { case (key, values) => (nodeToNode(key), values.map(nodeToNode)) },
      nodeHandlerMap = nodeHandlerMap.map { case ((node, t), handlers) => ((nodeToNode(node), t), handlers) },
      dialogHandlerMap = dialogHandlerMap.map { case ((node, t), handlers) => ((nodeToNode(node), t), handlers) },
      activityRootViewMap = activityRootViewMap.view.mapValues(_.map(nodeToNode)).toMap
    )
  }

  /**
   * STRUCTURAL METHOD
   */
  def sizeSummary: Map[String, Int] =
    Map(
      "localNodeMap" -> localNodeMap.size,
      "globalNodeMap" -> globalNodeMap.size,
      "nodeEdgeMap" -> nodeEdgeMap.values.map(_.size).sum,
      "nodeHandlerMap" -> nodeHandlerMap.size,
      "dialogHandlerMap" -> dialogHandlerMap.size,
      "activityRootViewMap" -> activityRootViewMap.values.map(_.size).sum)

  /**
   * STRUCTURAL METHOD
   */
  def getHeap: AFTDomain = copy(localNodeMap = Map())

  /**
   * STRUCTURAL METHOD
   *
   * currentWindowClasses is not really useful in determining whether there is interesting data we want to trace here.
   */
  def nonEmpty: Boolean =
    localNodeMap.nonEmpty || globalNodeMap.nonEmpty || nodeEdgeMap.nonEmpty || nodeEdgeRevMap.nonEmpty ||
      activityRootViewMap.nonEmpty || nodeHandlerMap.nonEmpty || dialogHandlerMap.nonEmpty

  /**
   * STRUCTURAL METHOD
   */
  private def equivTo(domain: AFTDomain): Boolean =
    localNodeMap == domain.localNodeMap &&
      globalNodeMap == domain.globalNodeMap &&
      currentWindowClasses == domain.currentWindowClasses &&
      nodeEdgeMap == domain.nodeEdgeMap &&
      activityRootViewMap == domain.activityRootViewMap &&
      nodeHandlerMap == domain.nodeHandlerMap &&
      dialogHandlerMap == domain.dialogHandlerMap

  override def equals(obj: Any): Boolean = {
    if (obj == null) return false
    if (super.equals(obj)) return true
    obj match {
      case domain: AFTDomain => equivTo(domain)
      case _ => false
    }
  }

  override def toString: String = sizeSummary.toString + "\n" + nodeEdgeMap.toString

  def getViewNodes(contextMethod: SootMethod, stmt: Stmt, local: Local): Iterable[ViewNode] = {
    getNodes(contextMethod, stmt, local).collect { case v: ViewNode => v }
  }

  def getNodes(contextMethod: SootMethod, stmt: Stmt, local: Local): Iterable[AbsNode] = {
    localNodeMap.flatMap { case (l, accessPaths) =>
      if (PreAnalyses.isAlias(local, l, stmt, stmt, contextMethod)) {
        accessPaths.data match {
          case Some(a) => a.vals
          case None => Set()
        }
      } else {
        Set()
      }
    }
  }

  def addEdge(parentNode: ViewNode, childNode: ViewNode): AFTDomain = {
    // FIXME: current view-node is over-approximate, thus a wrapper function that creates many nodes at runtime
    //        might be interpreted as returning the same abstract node, if there is no sufficient context info to
    //        differentiate them. Currently, we will not avoid such kind of recursive edges, but will detect them
    //        when making recursive graph traversal
    // assert(parentNode != childNode)
    copy(nodeEdgeMap = AFTDomain.addEdgeToMap(nodeEdgeMap, parentNode, childNode),
      nodeEdgeRevMap = AFTDomain.addEdgeToMap(nodeEdgeRevMap, childNode, parentNode))
  }

  def getOwnerActivities(contextMethod: SootMethod, stmt: Stmt, viewBase: Local): Set[SootClass] =
    getViewNodes(contextMethod, stmt, viewBase).flatMap(getOwnerActivities(contextMethod, stmt, _)).toSet

  def getOwnerDialogs(contextMethod: SootMethod, stmt: Stmt, viewBase: Local): Set[ViewNode] =
    getViewNodes(contextMethod, stmt, viewBase).flatMap(getOwnerDialogs(contextMethod, stmt, _)).toSet

  def getOwnerActivities(contextMethod: SootMethod, stmt: Stmt,
                         viewNode: ViewNode, visited: Set[ViewNode] = Set()): Set[SootClass] = {
    nodeEdgeRevMap.get(viewNode) match {
      case Some(edges) => edges.flatMap(parentNode => if (visited.contains(parentNode)) {
        None
      } else {
        getOwnerActivities(contextMethod, stmt, parentNode, visited + parentNode)
      })
      case None => activityRootViewMap.flatMap { case (clazz, nodes) =>
        if (nodes.contains(viewNode)) { Set(clazz) } else { Set() }
      }.toSet
    }
  }

  def getOwnerDialogs(contextMethod: SootMethod, stmt: Stmt,
                      viewNode: ViewNode, visited: Set[ViewNode] = Set()): Set[ViewNode] = {
    nodeEdgeRevMap.get(viewNode) match {
      case Some(edges) =>
        edges.flatMap(parentNode =>
          if (visited.contains(parentNode)) {
            Set()
          } else {
            getOwnerDialogs(contextMethod, stmt, parentNode, visited + parentNode)
          })
      case None => if (viewNode.sootClass.nonEmpty && Globals.appInfo.isDialogClass(viewNode.sootClass.get)) {
        Set(viewNode)
      } else {
        Set()
      }
    }
  }

  type A = AccessPath[AbsValSet[AbsNode]]

  def getAccessPath(l: Local): Option[A] = localNodeMap.get(l)

  def getAccessPath(ref: Ref): Option[A] =
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        globalNodeMap.get(cls) match {
          case Some(accessPath) => accessPath.get(fields)
          case None => None
        }
      case Ref.LocalRef(local, fields) =>
        localNodeMap.get(local) match {
          case Some(accessPath) => accessPath.get(fields)
          case None => None
        }
    }

  def withSubPath(ref: Ref, subPath: A): AFTDomain = {
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        copy(
          globalNodeMap = globalNodeMap.get(cls) match {
            case None => globalNodeMap + (cls -> AccessPath(None).add(fields, subPath))
            case Some(accessPath) => globalNodeMap + (cls -> accessPath.add(fields, subPath))
          }
        )
      case Ref.LocalRef(local, fields) =>
        copy(
          localNodeMap = localNodeMap.get(local) match {
            case None => localNodeMap + (local -> AccessPath(None).add(fields, subPath))
            case Some(accessPath) => localNodeMap + (local -> accessPath.add(fields, subPath))
          }
        )
    }
  }

  def updateUnifiedObjectNodes(ctxMethod: SootMethod, stmt: Stmt, instanceInvokeExpr: InstanceInvokeExpr): AFTDomain = {
    val baseLocal = instanceInvokeExpr.getBase.asInstanceOf[Local]
    updateLocalNonViewNodes(ctxMethod, stmt, baseLocal, {
      case n@UnifiedObjectNode(absName, attrs) =>
        UnifiedObjectAPI.invokeFrom(absName, attrs, instanceInvokeExpr) match {
          case Some(newAttrs) => UnifiedObjectNode(absName, newAttrs)
          case None => n
        }
      case n => n
    })
  }

  def setContentViewDialog(ctxMethod: SootMethod, stmt: Stmt, dialogLocal: Local, viewLocal: Local): AFTDomain = {
    var d = copy()
    for (viewNode <- getViewNodes(ctxMethod, stmt, viewLocal)) {
      d = d.withEdge(ctxMethod, stmt, dialogLocal, viewNode)
    }
    d
  }

  def setContentViewAct(ctxMethod: SootMethod, stmt: Stmt, actClass: SootClass, viewLocal: Local): AFTDomain = {
    var activityRootViewMap2 = activityRootViewMap
    for (viewNode <- getViewNodes(ctxMethod, stmt, viewLocal)) {
      activityRootViewMap2 = activityRootViewMap2 + (actClass -> Set(viewNode))
    }
    copy(
      activityRootViewMap = activityRootViewMap2
    )
  }

  def setId(ctxMethod: SootMethod, dialogLocal: Local, stmt: Stmt, newId: Int): AFTDomain = {
    val nodes = getViewNodes(ctxMethod, stmt, dialogLocal).toSet
    updateAllViewNodes(viewNode => {
      if (nodes.contains(viewNode)) {
        viewNode.copy(id = viewNode.id + newId)
      } else {
        viewNode
      }
    })
  }

  /**
   * @param optTraverser Applies to each inflated sub-node to add additional info e.g. the inlinde handlers to the domain.
   * @return
   */
  def inflateAFT(stmt: Stmt, node: ViewNode, view: AndroidView,
                 optTraverser: Option[Traverser]): AFTDomain = {
    var d = copy()
    if (view == null) {
      return d
    }
    for (child <- view.getChildren.asScala) {
      val childNode = ViewNode(stmt, id=Set(child.getId), sootClass = Some(child.getSootClass), androidView = child)
      d = optTraverser match {
        case Some(traverser) => traverser.withSubNode(d, childNode)
        case None => d
      }
      d = d.inflateAFT(stmt, childNode, child, optTraverser)
      d = d.addEdge(node, childNode)
    }
    d
  }

  def setHandlers(contextMethod: SootMethod, stmt: Stmt, l: Local,
                  eventType: EventType, handlers: Set[(SootMethod, SourceLoc)]): AFTDomain = {
    var d = copy()
    for (viewNode <- getViewNodes(contextMethod, stmt, l)) {
      d = d.setHandlers(viewNode, eventType, handlers)
    }
    d
  }

  def setHandlers(viewNode: ViewNode, eventType: EventType, handlers: Set[(SootMethod, SourceLoc)]): AFTDomain = {
    var nodeHandlerMap2 = nodeHandlerMap
    nodeHandlerMap2 += ((viewNode, eventType) -> handlers)
    copy(nodeHandlerMap = nodeHandlerMap2)
  }

  def addHandler(viewNode: ViewNode, eventType: EventType, handler: SootMethod, sourceLoc: SourceLoc): AFTDomain = {
    val newHandlers = nodeHandlerMap.get((viewNode, eventType)) match {
      case Some(handlers) => handlers.+((handler, sourceLoc))
      case None => Set((handler, sourceLoc))
    }
    copy(nodeHandlerMap = nodeHandlerMap + ((viewNode, eventType) -> newHandlers))
  }

  /**
   * Set dialog's POSITIVE/NEGATIVE/NEUTRAL button handler
   *
   * @param contextMethod The context of invocation
   * @param stmt Invocation statement
   * @param l DialogView local variable
   * @param handler Handler of button
   * @param dialogButtonType: If None, means unknown type -- we will set for all possible types
   * @return
   */
  def setDialogButtonHandler(contextMethod: SootMethod, stmt: Stmt, l: Local,
                             handler: SootMethod, dialogButtonType: Option[DialogButtonType.Value]): AFTDomain = {
    var d = copy()
    for (dialogViewNode <- getViewNodes(contextMethod, stmt, l)) {
      d = d.setDialogButtonHandler(dialogViewNode, handler, dialogButtonType)
    }
    d
  }

  private def setDialogButtonHandler(viewNode: ViewNode, handler: SootMethod,
                                     dialogButtonType: Option[DialogButtonType.Value]): AFTDomain = {
    var d = copy()
    dialogButtonType match {
      case Some(buttonType) =>
        d = d.setDialogButtonHandler(viewNode, buttonType, handler)
      case None =>
        for (buttonType <- DialogButtonType.values) {
          d = d.setDialogButtonHandler(viewNode, buttonType, handler)
        }
    }
    d
  }

  /**
   * @param viewNode FIXME: Currently we use ViewNode to wrap builder as well
   * @return
   */
  private def setDialogButtonHandler(viewNode: ViewNode, buttonType: DialogButtonType.Value,
                                     handler: SootMethod): AFTDomain = {
    val viewNodeClass = viewNode.sootClass.get
    if (Globals.appInfo.isDialogBuilderClass(viewNodeClass)) {
      var dialogHandlerMap2 = dialogHandlerMap
      dialogHandlerMap2 += ((viewNode, buttonType) -> Set(handler))
      copy(dialogHandlerMap = dialogHandlerMap2)
    } else {
      assert(Globals.appInfo.isDialogClass(viewNodeClass))
      var d = copy()
      for (buttonView <- findViewByButtonType(viewNode, buttonType)) {
        d = d.setHandlers(buttonView, EventType.click, Set((handler, SourceLoc.fromJavaLinked(handler))))
      }
      d
    }
  }

  def setDialogTitle(ctxMethod: SootMethod, stmt: Stmt, viewLocal: Local, param: Value): AFTDomain = {
    var d = copy()
    d = d.updateLocalViewNodes(ctxMethod, stmt, viewLocal, {
      case viewNode: ViewNode =>
        val newAttr = Set((AndroidView.ViewAttr.dialogTitle, param)).collect {
          case (attr, stringConstant: StringConstant) =>
            (attr, stringConstant.value)
        }
        viewNode.setAttributes(newAttr)
      case n => n
    })
    d
  }

  def setDialogMessage(ctxMethod: SootMethod, stmt: Stmt, viewLocal: Local, param: Value): AFTDomain = {
    var d = copy()
    d = d.updateLocalViewNodes(ctxMethod, stmt, viewLocal, {
      case viewNode: ViewNode =>
        val newAttr = Set((AndroidView.ViewAttr.dialogMessage, param)).flatMap {
          case (attr, stringConstant: StringConstant) =>
            Some((attr, stringConstant.value))
          case (attr, intConstant: IntConstant) =>
            Globals.appInfo.getStringResourceValueById(intConstant.value) match {
              case Some(s) =>
                Some((attr, s))
              case _ => None
            }
          case _ => None
        }
        viewNode.setAttributes(newAttr)
      case n => n
    })
    d
  }


  /**
    * ctxMethod {
    *   ...
    *   stmt: viewLocal.setLayoutParams(paramsLocal)
    *   ...
    * }
    */
  def setLayoutParams(ctxMethod: SootMethod, stmt: Stmt, viewLocal: Local, paramsLocal: Local): AFTDomain = {
    var d = copy()
    for (node <- getNodes(ctxMethod, stmt, paramsLocal)) {
      node match {
        case LayoutParamsNode(attrs) =>
          d = d.updateLocalViewNodes(ctxMethod, stmt, viewLocal, viewNode => viewNode.setAttributes(attrs))
        case _ =>
      }
    }
    d
  }

  /**
    * ctxMethod {
    *   ...
    *   stmt: paramsBase.__init__(height, width)
    *   ...
    * }
    */
  def initLayoutParams(ctxMethod: SootMethod, stmt: Stmt, paramsBase: Local, width: Value, height: Value): AFTDomain = {
    val newAttrs = List((width, AndroidView.ViewAttr.layout_width), (height, AndroidView.ViewAttr.layout_height)).collect {
      case (intConstant: IntConstant, attr) =>
        (attr, Constants.layoutParamIntToString(intConstant.value))
    }
    if (newAttrs.nonEmpty) {
      updateLocalNonViewNodes(ctxMethod, stmt, paramsBase, {
        case LayoutParamsNode(attrs) => LayoutParamsNode(attrs ++ newAttrs)
        case n => n
      })
    } else {
      this
    }
  }

  def getDialogButtonHandlers(node: ViewNode): Iterable[SootMethod] = {
    dialogHandlerMap.flatMap { case ((n, _), handlers) =>
      if (n == node) {
        handlers
      } else {
        Set()
      }
    }
  }

  def killRef(ref: Ref): AFTDomain =
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        copy(globalNodeMap = (fields, globalNodeMap.get(cls)) match {
          case (_, None) => globalNodeMap
          case (List(), _) => globalNodeMap - cls
          case (fields, Some(accessPath)) => globalNodeMap + (cls -> accessPath.kill(fields))
        })
      case Ref.LocalRef(local, fields) =>
        copy(localNodeMap = (fields, localNodeMap.get(local)) match {
          case (_, None) => localNodeMap
          case (List(), _) => localNodeMap - local
          case (fields, Some(accessPath)) => localNodeMap + (local -> accessPath.kill(fields))
        })
    }

  def withNode(ref: Ref, node: AbsNode): AFTDomain = {
    withNodes(ref, Set(node))
  }

  def withNodes(ref: Ref, nodes: Set[AbsNode]): AFTDomain = {
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        copy(
          globalNodeMap = if (nodes.nonEmpty) {
            globalNodeMap + (cls -> AccessPath(None).add(fields, AbsValSet(nodes)))
          } else {
            globalNodeMap
          }
        )
      case Ref.LocalRef(local, fields) =>
        copy(
          localNodeMap = if (nodes.nonEmpty) {
            localNodeMap + (local -> AccessPath(None).add(fields, AbsValSet(nodes)))
          } else {
            localNodeMap
          }
        )
    }
  }

  def newView(ref: Ref, sootClass: SootClass, stmt: Stmt): AFTDomain = {
    newView_(ref, sootClass, stmt)._1
  }

  private def newView_(ref: Ref, sootClass: SootClass, stmt: Stmt): (AFTDomain, ViewNode) = {
    val node = ViewNode(stmt, sootClass = Some(sootClass), androidView = null)
    var d = withNode(ref, node)
    if (Globals.appInfo.isDialogClass(sootClass)) {
      // https://developer.android.com/reference/android/content/DialogInterface
      // TODO: inflate existing built-in template instead?
      val buttons = List(
        ViewNode(stmt, buttonType = Some(DialogButtonType.POSITIVE)),
        ViewNode(stmt, buttonType = Some(DialogButtonType.NEGATIVE)),
        ViewNode(stmt, buttonType = Some(DialogButtonType.NEUTRAL)))
      for (childNode <- buttons) {
        d = d.addEdge(node, childNode)
      }
      (d, node)
    } else {
      (d, node)
    }
  }

  def newUnifiedObject(ref: Ref, sootClass: SootClass, stmt: Stmt): AFTDomain = {
    withNode(ref, UnifiedObjectAPI.newFrom(sootClass))
  }

  def newLayoutParams(ref: Ref): AFTDomain = {
    withNode(ref, LayoutParamsNode())
  }


  def dialogCreate(ref: Ref, sootClass: SootClass, stmt: Stmt, builderLocal: Local, contextMethod: SootMethod): AFTDomain = {
    var (d, dialogViewNode) = newView_(ref, sootClass, stmt)
    // Propagate button handler information from builder node to the view node
    for (builderNode <- getViewNodes(contextMethod, stmt, builderLocal)) {
      for (((node, buttonType), handlers) <- dialogHandlerMap) {
        if (node == builderNode) {
          for (handler <- handlers) {
            if (handler != null) {
              d = d.setDialogButtonHandler(dialogViewNode, handler, Some(buttonType))
            }
          }
        }
      }
    }
    d
  }

  def newAct(ref: Ref, sootClass: SootClass): AFTDomain = {
    withNode(ref, ActNode(sootClass = sootClass))
  }

  def newListener(ref: Ref, c: SootClass): AFTDomain = {
    withNode(ref, ListenerNode(c))
  }

  def findViewById(viewNode: ViewNode, id: Int): IterableOnce[ViewNode] = {
    // FIXME: without knowing the exact indices, this is going to be an over-approx
    (nodeEdgeMap.get(viewNode) match {
      case Some(edges) =>
        edges.flatMap(targetNode => findViewById(targetNode, id))
      case None => Iterable.empty
    }) ++ (if (viewNode.id.contains(id)) {
      Iterable.single(viewNode)
    } else {
      Iterable.empty
    })
  }

  def findViewByButtonType(viewNode: ViewNode, buttonType: DialogButtonType.Value): IterableOnce[ViewNode] = {
    (nodeEdgeMap.get(viewNode) match {
      case Some(edges) =>
        edges.flatMap(targetNode => findViewByButtonType(targetNode, buttonType))
      case None => Iterable.empty
    }) ++ (if (viewNode.buttonType.contains(buttonType)) {
      Iterable.single(viewNode)
    } else {
      Iterable.empty
    })
  }

  /**
   * FIXME: might be slow
   * @param parent
   * @param child
   * @return
   */
  def withEdge(contextMethod: SootMethod, stmt: Stmt, parent: Local, child: Local): AFTDomain = {
    var d = copy()
    for (parentNode <- getViewNodes(contextMethod, stmt, parent)) {
      for (childNode <- getViewNodes(contextMethod, stmt, child)) {
        d = d.addEdge(parentNode, childNode)
      }
    }
    d
  }

  // NOTE: repetition
  def withEdge(contextMethod: SootMethod, stmt: Stmt, parent: Local, childNode: ViewNode): AFTDomain = {
    var d = copy()
    for (parentNode <- getViewNodes(contextMethod, stmt, parent)) {
      d = d.addEdge(parentNode, childNode)
    }
    d
  }

  def toJSONObj: Object = Map[String, Object](
    "localNodeMap" -> localNodeMap.map { case (k, v) => (k.toString(), v.toJSONObj) },
    "globalNodeMap" -> globalNodeMap.map { case (k, v) => (k.toString, v.toJSONObj) },
    "nodeHandlerMap" -> nodeHandlerMap.map { case (k, v) => (k._1.nodeID, k._2.toString, v.map(_._1.getSignature).toList) },
    "dialogHandlerMap" -> dialogHandlerMap.map { case (k, v) => (k._1.nodeID, k._2.toString, v.map(_.getSignature).toList) },
  )
}

object AFTDomain {
  val top: AFTDomain = AFTDomain(Map(), Map(), Set(), Map(), Map(), Map(), Map(), Map())

  def addEdgeToMap(m: Map[ViewNode, Set[ViewNode]], from: ViewNode, to: ViewNode): Map[ViewNode, Set[ViewNode]] = {
    m.get(from) match {
      case Some(edges) =>
        m + (from -> (edges ++ Set(to)))
      case None =>
        m + (from -> Set(to))
    }
  }

  def mapToString[K, V](m: Map[K, V]): String =
    m.map { case (k, v) => "\t " + k + " -> " + v }.mkString("\n")

  def mergeMapOfSets[K, V](m1: Map[K, Set[V]], m2: Map[K, Set[V]]): Map[K, Set[V]] = {
    if (m1.equals(m2)) return m1
    mergeMaps(m1, m2, (m1: Set[V], m2: Set[V]) => m1 ++ m2)
  }

  /**
   * FIXME: This can be very slow (azoo-vbstatsfree.apk)
   */
  def mergeMaps[K, V](m1: Map[K, V], m2: Map[K, V], f: (V, V) => V): Map[K, V] = {
    (m1.keySet ++ m2.keySet).map(k => {
      if (m1.contains(k) && m2.contains(k)) {
        (k, f(m1(k), m2(k)))
      } else if (m1.contains(k)) {
        (k, m1(k))
      } else {
        (k, m2(k))
      }
    }).toMap
  }

  def mergeMapOfAccessPath[K, D <: AbsVal[D]](m1: Map[K, AccessPath[D]],
                                 m2: Map[K, AccessPath[D]]): Map[K, AccessPath[D]] = {
    if (m1.equals(m2)) return m1
    mergeMaps(m1, m2, (m1: AccessPath[D], m2: AccessPath[D]) => m1.merge(m2))
  }
}
