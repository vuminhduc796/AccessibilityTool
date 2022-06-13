/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import com.research.nomad.markii.Util.getJavaLineNumber
import com.research.nomad.markii.analyses.{InterProcDataAnalysis, PreVASCO}
import com.research.nomad.markii.dataflow.AbsNode.{ActNode, ListenerNode, ViewNode}
import com.research.nomad.markii.{Constants, Core, Util}
import io.github.izgzhen.msbase.{IOUtil, JsonUtil}
import presto.android.gui.listener.EventType

import scala.jdk.CollectionConverters._
import soot.jimple.internal.{JIdentityStmt, JimpleLocal}
import soot.jimple.{AssignStmt, CastExpr, InstanceFieldRef, InstanceInvokeExpr, IntConstant, InvokeExpr, NewExpr, ReturnStmt, StaticFieldRef, Stmt, ThisRef}
import soot.{Local, RefType, Scene, SootClass, SootMethod, Value}
import vasco.ProgramRepresentation

import scala.collection.mutable

/**
 * Implementation of abstract value propagation for VASCO DFA framework
 */
abstract class AbstractValuePropVASCO(core: Core, preVasco: PreVASCO, entryPoints: List[SootMethod])
  extends InterProcDataAnalysis[SootMethod, soot.Unit, AFTDomain] {

  type Domain = AFTDomain

  private val RETURN_LOCAL = new JimpleLocal("@return", null)

  private def setDialogButtonListener(buttonType: DialogButtonType.Value, invokeExpr: InvokeExpr, d: AFTDomain,
                                      ctxMethod: SootMethod, stmt: Stmt): AFTDomain = {
    invokeExpr.getArgs.asScala.map(_.getType).collectFirst {
      case refType: RefType if core.appInfo.isDialogOnClickListener(refType.getSootClass) => refType.getSootClass
    } match {
      case Some(listener) =>
        Util.getMethodByNameUnsafe(listener, "onClick") match {
          case Some(handler) => {
            val dialogBuilder = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
            d.setDialogButtonHandler(ctxMethod, stmt, dialogBuilder, handler, Some(buttonType))
          }
          case None => d
        }
      case _ => d
    }
  }

  def assigned(contextMethod: SootMethod, assignStmt: Stmt, ref: Ref,
               value: Value, ctx: Domain, input: Domain): Domain = {
    val killed = input.killRef(ref)
    value match {
      case castExpr: CastExpr =>
        assigned(contextMethod, assignStmt, ref, castExpr.getOp, ctx, input)
      case newExpr: NewExpr =>
        val sootClass = newExpr.getBaseType.getSootClass
        if (core.appInfo.hier.isSubclassOf(sootClass, Scene.v().getSootClass(Constants.androidViewClassName))) {
          killed.newView(ref, sootClass, assignStmt)
        } else if (core.appInfo.isDialogBuilderClass(sootClass)) {
          killed.newView(ref, sootClass, assignStmt)
        } else if (core.appInfo.isDialogClass(sootClass)) {
          killed.newView(ref, sootClass, assignStmt)
        } else if (core.appInfo.isViewEventListenerClass(sootClass)) {
          killed.newListener(ref, sootClass)
        } else if (core.appInfo.hier.isSubclassOf(sootClass, Constants.layoutParamsClass)) {
          killed.newLayoutParams(ref)
        } else if (UnifiedObjectAPI.isBaseClass(sootClass)) {
          killed.newUnifiedObject(ref, sootClass, assignStmt)
        } else if(core.appInfo.isDialogFragment(sootClass)) {
          killed.newView(ref, sootClass, assignStmt)
        } else {
          killed
        }
      case rhsLocal: Local =>
        ctx.getAccessPath(rhsLocal) match {
          case Some(accessPath) =>
            killed.withSubPath(ref, accessPath)
          case None => killed
        }
      case instanceFieldRef: InstanceFieldRef =>
        val rhsLocalRef = Ref.from(instanceFieldRef)
        input.getAccessPath(rhsLocalRef) match {
          case Some(accessPath) =>
            killed.withSubPath(ref, accessPath)
          case None => killed
        }
      case staticFieldRef: StaticFieldRef =>
        val rhsLocalRef = Ref.from(staticFieldRef)
        input.getAccessPath(rhsLocalRef) match {
          case Some(accessPath) =>
            killed.withSubPath(ref, accessPath)
          case None => killed
        }
      case invokeExpr: InstanceInvokeExpr =>
        val signature = invokeExpr.getMethod.getSignature
        val baseLocal = invokeExpr.getBase.asInstanceOf[Local]
        if (core.appInfo.isActivityFindViewById(invokeExpr.getMethod)) {
          invokeExpr.getArg(0) match {
            case intConstant: IntConstant =>
              // FIXME: over-approx of activity instances
              val activityClass = baseLocal.getType.asInstanceOf[RefType].getSootClass
              val subViews = mutable.Set[ViewNode]()
              val id = intConstant.value
              ctx.activityRootViewMap.get(activityClass) match {
                case Some(rootViews) =>
                  for (viewNode <- rootViews) {
                    subViews.addAll(ctx.findViewById(viewNode, id))
                  }
                case _ =>
              }
              return killed.withNodes(ref, subViews.toSet)
            case _ =>
          }
        }
        if (core.appInfo.isDialogFindViewById(invokeExpr.getMethod) || Constants.isViewFindViewById(invokeExpr.getMethod)) {
          invokeExpr.getArg(0) match {
            case intConstant: IntConstant =>
              val subViews = mutable.Set[ViewNode]()
              val id = intConstant.value
              for (viewNode <- ctx.getViewNodes(contextMethod, assignStmt, baseLocal)) {
                subViews.addAll(ctx.findViewById(viewNode, id))
              }
              return killed.withNodes(ref, subViews.toSet)
            case _ =>
          }
        }
        if (invokeExpr.getMethod.getName == "findViewById") {
//          println("Unhandled signature: " + signature)
        }
        if (Constants.isDialogBuilderCreate(signature)) {
          return killed.dialogCreate(
            ref, sootClass = invokeExpr.getType.asInstanceOf[RefType].getSootClass,
            assignStmt, baseLocal, contextMethod)
        }
        val subSig = invokeExpr.getMethod.getSubSignature
        val setButtionType = Constants.fromDialogBuilderSetButton(subSig)
        if (setButtionType.nonEmpty) {
          setDialogButtonListener(setButtionType.get, invokeExpr, input, contextMethod, assignStmt)
        } else if (Constants.isDialogSetTitle(invokeExpr.getMethod.getSignature)) {
          input.setDialogTitle(contextMethod, assignStmt, baseLocal, invokeExpr.getArg(0))
        } else if (Constants.isDialogSetMessage(invokeExpr.getMethod.getSignature)) {
          input.setDialogMessage(contextMethod, assignStmt, baseLocal, invokeExpr.getArg(0))
        } else if (Constants.isDialogBuilderSetAny(subSig)) {
          input // Don't kill for other builder setters
        } else if (signature == "<android.view.LayoutInflater: android.view.View inflate(int,android.view.ViewGroup,boolean)>") {
          // FIXME: other inflate signatures
          invokeExpr.getArg(0) match {
            case intConstant: IntConstant =>
              invokeExpr.getArg(1) match {
                case parentView: Local =>
                  val attachToRoot = invokeExpr.getArg(2).asInstanceOf[IntConstant].value != 0
                  inflate(killed, contextMethod, assignStmt, intConstant.value, ref, parentView, attachToRoot)
                case _ => killed
              }
            case _ => killed
          }
        } else if (invokeExpr.isInstanceOf[InstanceInvokeExpr] &&
                   UnifiedObjectAPI.isBaseClass(invokeExpr.getMethod.getDeclaringClass)) {
          // TODO: rewrite this whole thing with CustomState, use alias and analyze semantics
          assigned(contextMethod, assignStmt, ref, baseLocal, ctx, input)
        } else {
          killed
        }
      case _ => killed
    }
  }

//  private var maxLog = Some(100)
  private var maxLog: Option[Int] = None
  private var logStateCounter = 0
  private var logStateMethodCounters = mutable.Map[SootMethod, Int]()
  private val logStateInterval = 1000

  private def logState(method: SootMethod, unit: soot.Unit, d: Domain): Unit = {
    if (!core.isDebugMode) return
    if (logStateCounter == logStateInterval) {
//      println(logStateMethodCounters.toList.sortBy(_._2).takeRight(5))
      logStateMethodCounters = mutable.Map[SootMethod, Int]()
      logStateCounter = 0
//      println(s"worklist size: ${Instant.now.getEpochSecond}: ${worklist.size()}")
    } else {
      logStateCounter += 1
      logStateMethodCounters(method) = logStateMethodCounters.getOrElse(method, 0) + 1
    }
    if (method.getSignature != "<xvideo.furbie.ro.AsyncListActivity: void gopro()>") {
      return
    }
    if (maxLog.nonEmpty) {
      if (maxLog.get < 0) {
        throw new RuntimeException("Logging ends")
      } else {
        maxLog = Some(maxLog.get - 1)
      }
    }
    val idx = Util.getUnitIndex(method.getActiveBody.getUnits, unit)
    val obj = Map(
      "method" -> method.getSignature,
      "unit" -> unit.toString(),
      "unitIdx" -> idx,
      "domain" -> d.toJSONObj,
      "domainSize" -> d.sizeSummary
    )
    val json = JsonUtil.toJson(obj)
    IOUtil.write(json, "/tmp/markii-debug/" + method.getSignature + "@" + idx + ".json")
  }

  override def normalFlowFunction(contextMethod: SootMethod, unit: soot.Unit, d: Domain): Domain = {
    logState(contextMethod, unit, d)
    unit match {
      case assignStmt: AssignStmt =>
        val ref = Ref.from(assignStmt.getLeftOp)
        return assigned(contextMethod, assignStmt, ref, assignStmt.getRightOp, d, d)
      case stmt: JIdentityStmt =>
        val methodName = contextMethod.getName
        val methodClass = contextMethod.getDeclaringClass
        if (stmt.getRightOp.isInstanceOf[ThisRef] && core.appInfo.isActivity(methodClass) && methodName == Constants.runnerMethodName) {
          // HACK: This is a HACK
          val localRef = Ref.from(stmt.getLeftOp)
          val killed = d.killRef(localRef)
          return killed.newAct(localRef, methodClass)
        }
      case retStmt: ReturnStmt =>
        return assigned(contextMethod, retStmt, Ref.LocalRef(RETURN_LOCAL), retStmt.getOp, d, d)
      case _ =>
    }
    d
  }

  // <com.appbrain.AppBrainActivity: boolean onKeyDown(int,android.view.KeyEvent)> is not entered, taken as a local call instead
  // APK: examples/frauddroid-autumn.apk
  override def callEntryFlowFunction(contextMethod: SootMethod, m: SootMethod, callSite: soot.Unit, d: Domain): Domain = {
    val stmt = callSite.asInstanceOf[Stmt]
    val invokeExpr = stmt.getInvokeExpr
    var ret = if (preVasco.isStartWindowStmt(callSite.asInstanceOf[Stmt])) {
      topValue()
    } else {
      d.getHeap
    }
    // Set the current window class in the abstract state before entering into the lifecycle method
    ret = core.appInfo.getLifecycleMethodWindow(m) match {
      case Some(cls) => ret.copy(currentWindowClasses = Set(cls))
      case None => ret
    }
    if (m.hasActiveBody) {
      for (i <- 0 until invokeExpr.getArgCount) {
        try {
          ret = assigned(contextMethod, stmt, Ref.LocalRef(m.getActiveBody.getParameterLocal(i)), invokeExpr.getArg(i), d, ret)
        } catch {
          case _: RuntimeException =>
        }
      }
      invokeExpr match {
        case instanceInvokeExpr: InstanceInvokeExpr =>
          ret = assigned(contextMethod, stmt, Ref.LocalRef(m.getActiveBody.getThisLocal), instanceInvokeExpr.getBase, d, ret)
        case _ =>
      }
    }
    ret
  }

  // ???: How is the exit flow joined with the flow in the caller context? How is the caller context updated?
  override def callExitFlowFunction(contextMethod: SootMethod, m: SootMethod, unit: soot.Unit, d: Domain): Domain = {
    var ret = d.getHeap
    var lhs: Option[soot.Local] = None
    unit match {
      case assignStmt: AssignStmt =>
        lhs = Some(assignStmt.getLeftOp.asInstanceOf[Local])
        ret = assigned(contextMethod, assignStmt, Ref.LocalRef(lhs.get), RETURN_LOCAL, d, ret)
      case _ =>
    }
    unit.asInstanceOf[Stmt].getInvokeExpr match {
      case instanceInvokeExpr: InstanceInvokeExpr =>
        val base = instanceInvokeExpr.getBase.asInstanceOf[Local]
        if (instanceInvokeExpr.getMethod.hasActiveBody) {
          val thisLocal = instanceInvokeExpr.getMethod.getActiveBody.getThisLocal
          if (!lhs.contains(base)) { // FIXME: join them properly
            ret = assigned(contextMethod, unit.asInstanceOf[Stmt], Ref.LocalRef(base), thisLocal, d, ret)
          }
        }
      case _ =>
    }
    ret
  }

  /**
   * Traverse sub-nodes in an inflated abstract view tree
   */
  class InflateTraverser(window: Option[SootClass]) extends Traverser {
    override def withSubNode(d: AFTDomain, viewNode: ViewNode): AFTDomain = {
      var newDomain = d
      for ((eventType, methodInfo) <- viewNode.getInlineClickHandlers) {
        val windowClasses = window match {
          case Some(act) => List(act)
          case None => d.currentWindowClasses
        }
        for (cls <- windowClasses) {
          Util.getMethodByNameUnsafe(cls, methodInfo.getName) match {
            case Some(method) => {
              newDomain = setEventHandler(newDomain, cls, method, eventType, viewNode,
                                          SourceLoc(methodInfo.getFile, getJavaLineNumber(method)))
            }
            case None =>
          }
        }
      }
      newDomain
    }
  }

    /**
   * Compute the post-state after "inflate" invocation on pre-state (d)
   *
   * Reference: https://developer.android.com/reference/android/view/LayoutInflater#inflate(int,%20android.view.ViewGroup)
   */
  private def inflate(d: AFTDomain, contextMethod: SootMethod, stmt: Stmt, id: Int,
                      ref: Ref, parentView: Local, attachToRoot: Boolean): AFTDomain = {
    core.appInfo.findViewById(id) match {
      case Some(view) =>
        val viewNode = ViewNode(stmt, id = Set(id), androidView = view)
        val traverser = new InflateTraverser(None)
        // Set XML-declared handlers for each sub-node of the inflated view tree in the abstract state
        val newDomain = traverser.withSubNode(d, viewNode).inflateAFT(stmt, viewNode, view, Some(traverser)).withNode(ref, viewNode)
        if (attachToRoot) {
          newDomain.withEdge(contextMethod, stmt, parentView, viewNode)
        } else {
          newDomain
        }
      case None => d
    }
  }

  /**
   * NOTE: this is separated from AFTDomain.setContentViewDialog since it accesses the AndroidView -- which we need to
   * access the bind handlers including the sub-view during construction
   */
  def setContentViewDialog(d: AFTDomain, ctxMethod: SootMethod, stmt: Stmt, dialogLocal: Local, id: Int): AFTDomain = {
    core.appInfo.findViewById(id) match {
      case Some(androidView) =>
        val viewNode = ViewNode(stmt, id = Set(id, androidView.getId.toInt), androidView = androidView)
        d.inflateAFT(stmt, viewNode, androidView, optTraverser = Some(new InflateTraverser(None)))
          .withEdge(ctxMethod, stmt, dialogLocal, viewNode)
      case None => d
    }
  }

  /**
   * NOTE: this is separated from AFTDomain.setContentViewAct since it accesses the AndroidView -- which we need to
   * access the bind handlers including the sub-view during construction
   */
  def setContentViewAct(d: AFTDomain, stmt: Stmt, actClass: SootClass, id: Int): AFTDomain = {
    core.appInfo.findViewById(id) match {
      case Some(androidView) =>
        val viewNode = ViewNode(stmt, id = Set(id, androidView.getId.toInt), androidView = androidView)
        d.inflateAFT(stmt, viewNode, androidView, optTraverser = Some(new InflateTraverser(Some(actClass)))).copy(
          activityRootViewMap = d.activityRootViewMap + (actClass -> Set(viewNode))
        )
      case None => d
    }
  }

  /**
   * Compute the post-state after invocation of API that set event listener (first argument of the invocation)
   * of a view node (base instance of the invocation).
   *
   * Note that the listener is an instance of a class with event handler method(s).
   */
  def setEventListener(d: AFTDomain, contextMethod: SootMethod, invokeExpr: InstanceInvokeExpr,
                       stmt: Stmt, handlerSubSig: String, eventType: EventType): AFTDomain = {
    val receiver = invokeExpr.getBase.asInstanceOf[Local]
    var listeners: Set[SootClass] = invokeExpr.getArg(0) match {
      case local: Local =>
        d.getNodes(contextMethod, stmt, local).collect {
          // FIXME: sometimes, the listener returned from here is not valid
          case ListenerNode(listener) => listener
        }.toSet
      case _ => Set()
    }
    invokeExpr.getArg(0).getType match {
      case refType: RefType =>
        listeners = listeners + refType.getSootClass
      case _ =>
    }
    val handlers = listeners.map(cls => {
      cls.getMethodUnsafe(handlerSubSig)
    }).filter(m => m != null && m.isConcrete && m.hasActiveBody)

    for (handler <- handlers) {
      for (dialogNode <- d.getOwnerDialogs(contextMethod, stmt, receiver)) {
        core.controlFlowGraphManager.addViewHandlerToEventLoopDialog(dialogNode, handler) match {
          case Some((runner, invocation)) =>
            aftProgramRepresentation.refreshCFGcache(runner)
            onNewCall(runner, invocation)
          case None =>
        }
      }

      for (ownerActivity <- d.getOwnerActivities(contextMethod, stmt, receiver)) {
        // FIXME: continueButton has no owner activities
        // FIXME: adding handler invocation might make some context missing nodes when joining over feasible
        //        paths
        core.controlFlowGraphManager.addViewHandlerToEventLoopAct(ownerActivity, handler) match {
          case Some((runner, invocation)) =>
            aftProgramRepresentation.refreshCFGcache(runner)
            onNewCall(runner, invocation)
          case None =>
        }
      }
    }
    d.setHandlers(contextMethod, stmt, receiver, eventType,
                  handlers.map(handler => (handler, SourceLoc.fromJavaLinked(handler))))
  }

  /**
   * Add handler to the call-graph and abstract state
   */
  def setEventHandler(d: AFTDomain, windowClass: SootClass, handler: SootMethod,
                      eventType: EventType, viewNode: ViewNode, sourceLoc: SourceLoc): AFTDomain = {
    // FIXME: windowClass vs Activity? Maybe we can unify them?....since the virtual/fake method contains the constructed
    //  instance for all em'
    core.controlFlowGraphManager.addViewHandlerToEventLoopAct(windowClass, handler) match {
      case Some((runner, invocation)) =>
        aftProgramRepresentation.refreshCFGcache(runner)
        onNewCall(runner, invocation)
      case None =>
    }
    d.addHandler(viewNode, eventType, handler, sourceLoc)
  }

  override def callLocalFlowFunction(contextMethod: SootMethod, unit: soot.Unit, d: Domain): Domain = {
    logState(contextMethod, unit, d)
    unit match {
      case assignStmt: AssignStmt =>
        val ref = Ref.from(assignStmt.getLeftOp)
        assigned(contextMethod, assignStmt, ref, assignStmt.getRightOp, d, d)
      case _ =>
        val stmt = unit.asInstanceOf[Stmt]
        if (stmt.containsInvokeExpr()) {
          val invokeExpr = stmt.getInvokeExpr
          if (invokeExpr.getMethod.getName == "addView" &&
            invokeExpr.getMethod.getDeclaringClass.getName == "android.view.ViewGroup") {
            val parentView = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase
            val childView = invokeExpr.getArg(0)
            return d.withEdge(contextMethod, stmt, parentView.asInstanceOf[Local], childView.asInstanceOf[Local])
          }
          val subSig = invokeExpr.getMethod.getSubSignature
          val setButtionType = Constants.fromDialogBuilderSetButton(subSig)
          if (setButtionType.nonEmpty) {
            return setDialogButtonListener(setButtionType.get, invokeExpr, d, contextMethod, stmt)
          }
          if (Constants.isDialogSetButton(invokeExpr.getMethod.getSignature)) {
            invokeExpr.getArgs.asScala.map(_.getType).collectFirst {
              case refType: RefType if core.appInfo.isDialogOnClickListener(refType.getSootClass) => refType.getSootClass
            } match {
              case Some(listener) =>
                Util.getMethodByNameUnsafe(listener, "onClick") match {
                  case Some(handler) => {
                    val local = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
                    return d.setDialogButtonHandler(contextMethod, stmt, local, handler, None)
                  }
                  case None =>
                }
              case _ =>
            }
          }
          if (invokeExpr.getMethod.getSubSignature == "void setOnClickListener(android.view.View$OnClickListener)") {
            return setEventListener(d, contextMethod, invokeExpr.asInstanceOf[InstanceInvokeExpr], stmt, "void onClick(android.view.View)", EventType.click)
          }
          if (invokeExpr.getMethod.getSubSignature == "void setOnTouchListener(android.view.View$OnTouchListener)") {
            return setEventListener(d, contextMethod, invokeExpr.asInstanceOf[InstanceInvokeExpr], stmt, "boolean onTouch(android.view.View,android.view.MotionEvent)", EventType.touch)
          }
          if (invokeExpr.getMethod.getSignature == "<android.view.View: void setId(int)>") {
            val dialogBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
            invokeExpr.getArg(0) match {
              case intConstant: IntConstant => return d.setId(contextMethod, dialogBase, stmt, intConstant.value)
              case _ =>
            }
          }
          if (invokeExpr.getMethod.getName == "setLayoutParams") {
            if (invokeExpr.getMethod.getSignature == "<android.view.View: void setLayoutParams(android.view.ViewGroup$LayoutParams)>") {
              val viewBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
              val paramsLocal = invokeExpr.getArg(0).asInstanceOf[Local]
              return d.setLayoutParams(contextMethod, stmt, viewBase, paramsLocal)
            }
//            println("Unhandled: " + invokeExpr.getMethod.getSignature)
          }
          if (invokeExpr.getMethod.getName == "setTitle") {
            if(Constants.isDialogSetTitle(invokeExpr.getMethod.getSignature)) {
              val viewBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
              val param = invokeExpr.getArg(0)
              return d.setDialogTitle(contextMethod, stmt, viewBase, param)
            }
          }
          if (invokeExpr.getMethod.getName == "setMessage") {
            if(Constants.isDialogSetMessage(invokeExpr.getMethod.getSignature)) {
              val viewBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
              val param = invokeExpr.getArg(0)
              return d.setDialogMessage(contextMethod, stmt, viewBase, param)
            }
          }
          // FIXME: improve precision, handle View argument
          // FIMXE: sub-class won't get the correct predicat here
          if (core.appInfo.isActivitySetContentViewWithInt(invokeExpr.getMethod)) {
            invokeExpr.getArg(0) match {
              case intConstant: IntConstant => return setContentView(contextMethod, d, invokeExpr, stmt, Left(intConstant.value))
              case _ =>
            }
          }
          if (core.appInfo.isActivitySetContentViewWithView(invokeExpr.getMethod)) {
            return setContentView(contextMethod, d, invokeExpr, stmt, Right(invokeExpr.getArg(0).asInstanceOf[Local]))
          }
          if (core.appInfo.isDialogSetContentViewWithInt(invokeExpr.getMethod)) {
            val dialogBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
            invokeExpr.getArg(0) match {
              case intConstant: IntConstant =>
                return setContentViewDialog(d, contextMethod, stmt, dialogBase, intConstant.value)
              case _ =>
            }
          }
          if (core.appInfo.isDialogSetContentViewWithView(invokeExpr.getMethod)) {
            val dialogBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
            return d.setContentViewDialog(contextMethod, stmt, dialogBase, invokeExpr.getArg(0).asInstanceOf[Local])
          }
          if (core.appInfo.hier.isSubclassOf(invokeExpr.getMethod.getDeclaringClass, Constants.layoutParamsClass)) {
            if (invokeExpr.getMethod.getName == "<init>") {
              val paramsBase = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
              if (invokeExpr.getMethod.getSubSignature == "void <init>(int,int)") {
                return d.initLayoutParams(contextMethod, stmt, paramsBase, invokeExpr.getArg(0), invokeExpr.getArg(1))
              }
//              println("Unhandled: " + invokeExpr.getMethod.getSignature)
            }
          }
          if (core.appInfo.hier.isSubclassOf(invokeExpr.getMethod.getDeclaringClass, Constants.dialogFragmentClass)){
            if (invokeExpr.getMethod.getSubSignature == "void show(androidx.fragment.app.FragmentManager,java.lang.String)") {
              preVasco.showDialogInvocations.put(stmt, invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local])
            }
          }
          invokeExpr match {
            case instanceInvokeExpr: InstanceInvokeExpr =>
              val sootClass = instanceInvokeExpr.getMethod.getDeclaringClass
              if (UnifiedObjectAPI.isBaseClass(sootClass)) {
                return d.updateUnifiedObjectNodes(contextMethod, stmt, instanceInvokeExpr)
              }
            case _ =>
          }
        }
        d
    }
  }

  private def setContentView(contextMethod: SootMethod, d: AFTDomain, invokeExpr: InvokeExpr,
                             stmt: Stmt, viewArg: Either[Int, Local]): AFTDomain = {
    val nodes = d.getNodes(contextMethod, stmt, invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local])
    var output = d
    for (node <- nodes) {
      node match {
        case ActNode(sootClass) =>
          viewArg match {
            case Left(id) => output = setContentViewAct(output, stmt, sootClass, id)
            case Right(viewLocal) => output = output.setContentViewAct(contextMethod, stmt, sootClass, viewLocal)
          }
        case _ => // TODO: WebView etc.
      }
    }
    output
  }

  override def boundaryValue(m: SootMethod): Domain = topValue()

  override def copy(d: Domain): Domain = d

  override def meet(d1: Domain, d2: Domain): Domain = d1.meet(d2)

  private val aftProgramRepresentation = new AFTProgramRepresentation(entryPoints)
  override def programRepresentation(): ProgramRepresentation[SootMethod, soot.Unit] = aftProgramRepresentation

  override def topValue(): Domain = AFTDomain.top
}
