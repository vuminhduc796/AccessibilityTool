package com.research.nomad.markii

import com.research.nomad.markii.analyses.PreVASCO
import com.research.nomad.markii.dataflow.AbsNode.ViewNode
import com.research.nomad.markii.dataflow.{AFTDomain, AbsAttr, AbsNode, DialogButtonType}
import presto.android.MethodNames
import presto.android.gui.wtg.util.WTGUtil
import presto.android.xml.AndroidView
import soot.{Local, RefType, Scene, SootMethod}
import soot.jimple.{InstanceInvokeExpr, Stmt, StringConstant}
import vasco.DataFlowSolution

import scala.collection.mutable
import scala.jdk.CollectionConverters._

class PostAnalysis(core: Core, vascoSolution: DataFlowSolution[soot.Unit, AFTDomain],
                   outputPath: String, preVASCO: PreVASCO) {
  private val analyzedHandlers = mutable.Set[SootMethod]()
  val writer: FactsWriter = new FactsWriter(outputPath)
  private val appInfo = core.appInfo

  def run(): Unit = {
    for (service <- appInfo.getServices) {
      writer.writeFact(FactsWriter.Fact.serviceClass, service)
      val names = service.getName.split("\\.")
      writer.writeFact(FactsWriter.Fact.serviceClassLastName, service, names.last)
    }

    for ((handler, reached, target) <- preVASCO.getStartActivityFacts) {
      writer.writeFact(FactsWriter.Fact.startActivity, handler, reached, target)
    }

    for (activityClass <- appInfo.allActivities) {
      val onCreate = appInfo.hier.virtualDispatch(MethodNames.onActivityCreateSubSig, activityClass)
      if (onCreate != null) {
        writer.writeFact(FactsWriter.Fact.lifecycleMethod, activityClass, "onCreate", onCreate)
      }

      val onDestroy = appInfo.hier.virtualDispatch(MethodNames.onActivityDestroySubSig, activityClass)
      if (onDestroy != null) {
        writer.writeFact(FactsWriter.Fact.lifecycleMethod, activityClass, "onDestroy", onDestroy)
      }
      if (appInfo.hier.isSubclassOf(activityClass, Constants.prefActivity)) {
        writer.writeFact(FactsWriter.Fact.preferenceActivity, activityClass)
      }
    }

    // Write more constraints
    writeFactsPostVASCO()
  }

  private def analyzeViewNode(viewNode: ViewNode, windowNode: Option[ViewNode] = None): Unit = {
    val nodeID = windowNode match {
      case Some(n) => n.nodeID // elf-ns
      case None => viewNode.nodeID
    }
    viewNode.id.foreach(id => {
      appInfo.getIdName(id) match {
        case Some(idName) =>
          writer.writeFact(FactsWriter.Fact.idName, idName, nodeID)
          if (Constants.isAdIdName(idName)) {
            writer.writeFact(FactsWriter.Fact.adViewIdName, idName)
          }
        case None =>
      }
    })
    // TODO: analyze the mutations of default values
    var hasContentDescription = false
    for ((attrib, value) <- viewNode.getAttrs) {
      if (value != null) {
        attrib match {
          case AndroidView.ViewAttr.layout_height =>
            writer.writeDimensionFact(FactsWriter.Fact.layoutHeight, value, nodeID)
          case AndroidView.ViewAttr.layout_width =>
            writer.writeDimensionFact(FactsWriter.Fact.layoutWidth, value, nodeID)
          case AndroidView.ViewAttr.textSize =>
            writer.writeDimensionFact(FactsWriter.Fact.textSize, value, nodeID)
          case AndroidView.ViewAttr.background =>
            writer.writeFact(FactsWriter.Fact.background, value, nodeID)
          case AndroidView.ViewAttr.text =>
            writer.writeFact(FactsWriter.Fact.textContent, value, nodeID)
            if (value.toLowerCase().contains("rec")) {
              writer.writeFact(FactsWriter.Fact.recordButton, nodeID)
            }
            if (value.toLowerCase().contains("continue")) {
              writer.writeFact(FactsWriter.Fact.actionButton, nodeID)
            }
          case AndroidView.ViewAttr.dialogTitle =>
            writer.writeFact(FactsWriter.Fact.dialogTitle, value, nodeID)
          case AndroidView.ViewAttr.dialogMessage =>
            writer.writeFact(FactsWriter.Fact.dialogMessage, value, nodeID)
          case AndroidView.ViewAttr.contentDescription => hasContentDescription = true
          case _ =>
        }
      }
    }
    for ((attrib, value) <- viewNode.getAppAttrs) {
      if (value != null) {
        writer.writeFact(FactsWriter.Fact.withName(attrib.name()), nodeID, value)
      }
    }
    viewNode.sootClass match {
      case Some(c) =>
        if (!hasContentDescription && appInfo.hier.isSubclassOf(c, Constants.imageViewClass)) {
          writer.writeFact(FactsWriter.Fact.imageHasNoContentDescription, nodeID)
        }
        if (Constants.isAdViewClass(c)) {
          writer.writeFact(FactsWriter.Fact.adViewClass, c)
        }
        writer.writeFact(FactsWriter.Fact.viewClass, c.getName, nodeID)
        if (appInfo.hier.isSubclassOf(c, Constants.buttonViewClass)) {
          writer.writeFact(FactsWriter.Fact.buttonView, nodeID)
        }
        if (appInfo.isDialogClass(c)) {
          writer.writeFact(FactsWriter.Fact.dialogView, nodeID,
            core.controlFlowGraphManager.getMethodOf(viewNode.allocSite))
        }
      case None =>
    }
  }

  private def writeFactsPostVASCO(): Unit = {
    for (act <- core.appInfo.allActivities) {
      for ((handler, event) <- core.appInfo.getActivityHandlers(act)) {
        analyzeAnyHandlerPostVASCO(handler)
        writer.writeFact(FactsWriter.Fact.activityEventHandler, event, handler, act)
        analyzeActivityHandlerPostVasco(handler)
      }

      val lifecycleMethods = List(
        act.getMethodUnsafe(MethodNames.onActivityCreateSubSig),
        act.getMethodUnsafe(MethodNames.onActivityStartSubSig)
      )
      for (m <- lifecycleMethods) {
        if (m != null) {
          analyzeAnyHandlerPostVASCO(m)
          analyzeActivityHandlerPostVasco(m)
        }
      }
    }

    for (handler <- appInfo.getAllHandlers) {
      analyzeAnyHandlerPostVASCO(handler)
    }

    for (method <- core.controlFlowGraphManager.dialogHandlerToAnalyze) {
      analyzeActivityHandlerPostVasco(method)
    }

    if (appInfo.mainActivity != null) {
      writer.writeFact(FactsWriter.Fact.mainActivity, appInfo.mainActivity)
    }
    val newlpMainActivity = Scene.v.getSootClassUnsafe("com.revlwp.wallpaper.newlp.MainActivity")
    if (newlpMainActivity != null) {
      writer.writeFact(FactsWriter.Fact.mainActivity, newlpMainActivity)
    }

    for ((action, m) <- appInfo.getIntents) {
      writer.writeFact(FactsWriter.Fact.intentFilter, action, m)
    }
  }

  private def analyzeActivityHandlerPostVasco(handler: SootMethod): Unit = {
    for (endpoint <- core.icfg.getEndPointsOf(handler).asScala) {
      val aftDomain = vascoSolution.getValueAfter(endpoint)
      if (aftDomain != null) {
        // TODO: inspect view nodes at the end of each activity handler
        // NOTE: there is extra computation, but do we care?
        for ((node, children) <- aftDomain.nodeEdgeMap) {
          analyzeViewNode(node)
          for (child <- children) {
            writer.writeFact(FactsWriter.Fact.containsView, node.nodeID, child.nodeID)
            analyzeViewNode(child)
          }
        }
      }
    }
  }

  private def analyzeAnyHandlerPostVASCO(handler: SootMethod): Unit = {
    if (analyzedHandlers.contains(handler)) {
      return
    }
    analyzedHandlers.add(handler)
    val reachedMethods = core.callGraphManager.reachableMethods(handler)

    // Analyze the end-points
    for (endpoint <- core.icfg.getEndPointsOf(handler).asScala) {
      val aftDomain = vascoSolution.getValueAfter(endpoint)
      if (aftDomain != null) {
        for (((viewNode, eventType), eventHandlers) <- aftDomain.nodeHandlerMap) {
          for ((eventHandler, sourceLoc) <- eventHandlers) {
            writer.writeFact(FactsWriter.Fact.eventHandler, eventType, eventHandler, viewNode.nodeID)
            writer.writeFact(FactsWriter.Fact.methodLineNumber,
              eventHandler,
              sourceLoc.file,
              sourceLoc.lineNumber,
              eventHandler.getDeclaringClass,
              viewNode.nodeID)
            analyzeAnyHandlerPostVASCO(eventHandler)
          }
        }
        for ((act, nodes) <- aftDomain.activityRootViewMap) {
          for (viewNode <- nodes) {
            writer.writeFact(FactsWriter.Fact.rootView, act, viewNode.nodeID)
          }
        }
      }
    }

    // Analyze each statements in reached method
    // FIXME: performance
    for (reached <- reachedMethods) {
      if (reached.getDeclaringClass.isApplicationClass && reached.isConcrete && reached.hasActiveBody) {
        for ((srcClass, intents) <- Ic3Manager.getIntents(reached)) {
          for (intent <- intents) {
            if (intent.getComponentClass != null && intent.getComponentClass.nonEmpty) {
              val targetAct = Scene.v().getSootClass(intent.getComponentClass)
              writer.writeFact(FactsWriter.Fact.startActivity, handler, reached, targetAct)
            }
            if (intent.getAction != null && intent.getAction.equals("android.intent.action.VIEW")) {
              if (intent.getDataScheme != null && intent.getDataScheme.equals("market")) {
                writer.writeFact(FactsWriter.Fact.startViewActivityOfMarketHost, handler, reached);
              } else {
                writer.writeFact(FactsWriter.Fact.startViewActivityOfSomeHosts, handler, reached);
              }
            }
          }
        }

        for (unit <- reached.getActiveBody.getUnits.asScala) {
          val stmt = unit.asInstanceOf[Stmt]
          if (stmt.containsInvokeExpr()) {
            val invokeExpr = stmt.getInvokeExpr
            val invokedMethod = Util.getMethodUnsafe(invokeExpr)
            val aftDomain = vascoSolution.getValueBefore(stmt)
            if (WTGUtil.v.isActivityFinishCall(stmt)) {
              invokeExpr match {
                case instanceInvokeExpr: InstanceInvokeExpr =>
                  val actClass = instanceInvokeExpr.getBase.getType.asInstanceOf[RefType].getSootClass
                  // FIXME: reachability
                  writer.writeFact(FactsWriter.Fact.finishActivity, handler, reached, actClass)
                case _ =>
              }
            }
            if (invokedMethod != null) {
              if (Constants.isDialogDismiss(invokedMethod.getSignature)) {
                val dialog = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.asInstanceOf[Local]
                if (aftDomain != null) {
                  // NOTE: We can combine the for-loops here
                  for (dialogNode <- aftDomain.getViewNodes(reached, stmt, dialog)) {
                    writer.writeFact(FactsWriter.Fact.dismiss, handler, dialogNode.nodeID)
                  }
                }
              }
              // FIXME: frauddroid-gba.apk "<android.app.Activity: void showDialog(int)>" and onPrepareDialog, onCreateDialog
              // 1. localNodeMap should include the dialogNode that was initialized in previous lines
              // 2. iterate dialogHandlerToAnalyze
              if (aftDomain != null) {
                preVASCO.getShowDialogInvocations(stmt) match {
                  case Some(dialogBase) => {
                    for (dialogNode <- aftDomain.getViewNodes(reached, stmt, dialogBase)) {
                      writer.writeFact(FactsWriter.Fact.dialogView, dialogNode.nodeID, core.controlFlowGraphManager.getMethodOf(dialogNode.allocSite))
                      writer.writeFact(FactsWriter.Fact.showDialog, handler, reached, dialogNode.nodeID)
                      // Write fact about dialog's YES/NO buttons' handlers
                      for (buttonType <- DialogButtonType.values) {
                        for (childNode <- aftDomain.findViewByButtonType(dialogNode, buttonType)) {
                          writer.writeFact(FactsWriter.Fact.dialogViewButton, dialogNode.nodeID,
                            childNode.nodeID, buttonType.toString)
                        }
                      }
                    }
                  }
                  case _ =>
                }
              }
              for(dialogHandler <- core.controlFlowGraphManager.dialogHandlerToAnalyze){
                analyzeAnyHandlerPostVASCO(dialogHandler)
              }
              if (invokedMethod.getSignature == "<com.google.ads.consent.ConsentInformation: void setConsentStatus(com.google.ads.consent.ConsentStatus)>") {
                writer.writeFact(FactsWriter.Fact.setStatus, handler, reached)
              }
              if (invokedMethod.getSignature == "<com.google.ads.consent.ConsentInformation: void requestConsentInfoUpdate(java.lang.String[],com.google.ads.consent.ConsentInfoUpdateListener)>") {
                val updateListenerType = invokeExpr.getArg(1).getType.asInstanceOf[RefType]
                val onConsentInfoUpdated = updateListenerType.getSootClass.getMethodUnsafe("void onConsentInfoUpdated(com.google.ads.consent.ConsentStatus)")
                if (onConsentInfoUpdated != null) {
                  writer.writeFact(FactsWriter.Fact.setConsetInfoUpdateHandler, handler, reached, onConsentInfoUpdated)
                }
              }
              if (invokedMethod.getSignature == "<android.os.BaseBundle: void putString(java.lang.String,java.lang.String)>") {
                (invokeExpr.getArg(0), invokeExpr.getArg(1)) match {
                  case (arg0: StringConstant, arg1: StringConstant) =>
                    if (arg0.value == "npa" && arg1.value == "1") {
                      writer.writeFact(FactsWriter.Fact.setNPA, handler)
                    }
                  case _ =>
                }
              }

              if (invokedMethod.getSignature == "<com.waps.AdView: void <init>(android.content.Context,android.widget.LinearLayout)>" ||
                invokedMethod.getSignature == "<com.waps.MiniAdView: void <init>(android.content.Context,android.widget.LinearLayout)>") {
                val layout = invokeExpr.getArg(1).asInstanceOf[Local]
                val aftDomain = vascoSolution.getValueBefore(stmt)
                if (aftDomain != null) {
                  for (node <- aftDomain.getViewNodes(reached, stmt, layout)) {
                    for (idName <- appInfo.getIdName(node)) {
                      writer.writeFact(FactsWriter.Fact.adViewIdName, idName)
                    }
                  }
                }
              }

              val invokedMethodClass = invokedMethod.getDeclaringClass
              if (invokedMethodClass.getName == "android.media.AudioRecord" && invokedMethod.getName == "read") {
                writer.writeFact(FactsWriter.Fact.readAudio, handler, reached)
              }
              if (invokedMethodClass.getName == "java.lang.Class" && invokedMethod.getName == "getDeclaredMethod") {
                writer.writeFact(FactsWriter.Fact.invokesReflectiveAPI, handler, reached)
              }
              if (invokedMethodClass.getName == "com.google.ads.consent.ConsentForm" && invokedMethod.getName == "load") {
                writer.writeFact(FactsWriter.Fact.loadGoogleConsentForm, handler, reached)
              }
              if (invokedMethodClass.getName == "androidx.work.WorkManager" && invokedMethod.getName == "enqueue") {
                val request = invokeExpr.getArg(0).asInstanceOf[Local]
                val aftDomain = vascoSolution.getValueBefore(stmt)
                if (aftDomain != null) {
                  for (node <- aftDomain.getNodes(reached, stmt, request)) {
                    node match {
                      case AbsNode.UnifiedObjectNode(absName, absAttrs) =>
                        val doWork = absAttrs("workerClass").asInstanceOf[AbsAttr.ClassVal].c.getMethodByName("doWork")
                        writer.writeFact(FactsWriter.Fact.withName("enqueued" + absName), handler, reached, doWork)
                        analyzeAnyHandlerPostVASCO(doWork)
                    }
                  }
                }
              }
              if (invokedMethodClass.getName == "android.webkit.WebView" && invokedMethod.getName == "loadUrl") {
                var arg0 = "ANY"
                invokeExpr.getArg(0) match {
                  case strConstant: StringConstant =>
                    arg0 = strConstant.value
                  case _ =>
                }
                writer.writeFact(FactsWriter.Fact.loadWebViewUrl, handler, reached, arg0)
              }
              if (invokedMethodClass.getName == "com.tongqu.client.utils.Downloader" && invokedMethod.getName == "getInst") {
                writer.writeFact(FactsWriter.Fact.downloadApp, handler, reached)
              }
              // NOTE: the "reached" field here has a different semantics than gator version
              if (Constants.isAdMethod(invokedMethod)) {
                writer.writeFact(FactsWriter.Fact.showAd, handler, invokedMethod)
              }
              if (Constants.isSuspiciousAdMethod(invokedMethod)) {
                writer.writeFact(FactsWriter.Fact.showSuspiciousAd, handler, reached)
              }
              if (Constants.isInterstitialAdMethod(invokedMethod)) {
                writer.writeFact(FactsWriter.Fact.showInterstitialAd, handler, reached)
              }
              if (Constants.isSuspiciousInterstitialAdMethod(invokedMethod)) {
                writer.writeFact(FactsWriter.Fact.showSuspiciousInterstitialAd, handler, reached)
              }
            }
          }
        }
      }
    }
  }
}
