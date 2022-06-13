/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii

import com.research.nomad.markii.Constants.{activityClasses, androidDialogOnClickListenerClass, dialogClassNames, dialogFragmentClass, receiverClass, serviceClass, viewEventListenerClasses}
import com.research.nomad.markii.dataflow.AbsNode.ViewNode
import presto.android.Hierarchy
import presto.android.gui.IDNameExtractor
import presto.android.xml.{AndroidView, XMLParser}
import soot.{Scene, SootClass, SootMethod}

import scala.collection.mutable
import scala.jdk.CollectionConverters._

class AppInfo {
  // Constructor
  val hier: Hierarchy = Hierarchy.v()
  private val xmlParser: XMLParser = XMLParser.Factory.getXMLParser

  private val allHandlers = mutable.Set[SootMethod]()
  val allActivities: Set[SootClass] = hier.frameworkManaged.keySet().asScala.filter(c =>
    hier.applicationActivityClasses.contains(c) && !c.isAbstract).toSet
  val mainActivity: SootClass = xmlParser.getMainActivity

  init()

  def findViewById(id: Int): Option[AndroidView] = xmlParser.findViewById(id) match {
    case null => None
    case v => Some(v)
  }

  def getStringResourceValueById(id: Int): Option[String] = xmlParser.getStringValue(id) match {
    case null => None
    case s => Some(s)
  }

  private def initAllHandlers(): Unit = {
    for (c <- Scene.v().getApplicationClasses.asScala) {
      if (c.isConcrete && Constants.guiClasses.exists(listener => hier.isSubclassOf(c, listener))) {
        for (m <- c.getMethods.asScala) {
          if (m.hasActiveBody && m.getName.startsWith("on")) {
            allHandlers.add(m)
          }
        }
      }
    }

    for (receiver <- xmlParser.getReceivers.asScala) {
      if (receiver != null) {
        val curCls = Scene.v.getSootClassUnsafe(receiver)
        if (curCls != null && curCls.isConcrete && hier.isSubclassOf(curCls, Scene.v().getSootClass("android.content.BroadcastReceiver"))) {
          val m = curCls.getMethodByNameUnsafe("onReceive")
          if (m != null && m.hasActiveBody) {
            allHandlers.add(m)
          }
        }
      }
    }
  }

  def init(): Unit = {
    initAllHandlers()
  }

  def getAllHandlers: Set[SootMethod] = allHandlers.toSet

  def getActivityHandlers(activity: SootClass): Map[SootMethod, String] = {
    Constants.activityHandlerSubsigs.flatMap { case (sig, event) =>
      val c = hier.matchForVirtualDispatch(sig, activity)
      if (c != null && c.isApplicationClass) {
        Some((c.getMethod(sig), event))
      } else {
        None
      }
    }
  }

  def getIntents: List[(String, SootMethod)] = {
    var ret = List[(String, SootMethod)]()
    for ((className, filters) <- xmlParser.getIntentFilters.asScala) {
      try {
        val curCls = Scene.v.getSootClass(className)
        if (curCls != null && curCls.isConcrete) {
          for (filter <- filters.asScala) {
            for (action <- filter.getActions.asScala) {
              val m = curCls.getMethodByNameUnsafe("onReceive")
              if (m != null) {
                ret :+= (action, m)
              }
            }
          }
        }
      } catch {
        case ignored: NullPointerException =>
      }
    }
    ret
  }

  def getServices: List[SootClass] = {
    var services = List[SootClass]()
    for (service <- xmlParser.getServices.asScala) {
      if (service != null) {
        val curCls = Scene.v.getSootClassUnsafe(service)
        if (curCls != null && curCls.isConcrete) {
          services :+= curCls
        }
      }
    }
    services
  }

  def getIdName(id: Int): Option[String] = {
    val idName = IDNameExtractor.v.idName(id)
    if (idName != null && idName.length > 0) {
      Some(idName)
    } else {
      None
    }
  }

  def getIdName(node: ViewNode): Set[String] = {
    node.id.flatMap(i => getIdName(i))
  }

  def isActivity(c: SootClass): Boolean = activityClasses.exists(activityClass => hier.isSubclassOf(c, activityClass))
  def isService(c: SootClass): Boolean = hier.isSubclassOf(c, serviceClass)
  def isReceiver(c: SootClass): Boolean = hier.isSubclassOf(c, receiverClass)
  def isDialogOnClickListener(c: SootClass): Boolean = hier.isSubclassOf(c, androidDialogOnClickListenerClass)

  def isViewEventListenerClass(sootClass: SootClass): Boolean =
    viewEventListenerClasses.exists(cls => hier.isSubclassOf(sootClass, cls))
  def isDialogBuilderClass(sootClass: SootClass): Boolean =
    dialogClassNames.exists(x => hier.isSubclassOf(sootClass, Scene.v().getSootClass(x + "$Builder")))

  def isDialogClass(sootClass: SootClass): Boolean =
    dialogClassNames.exists(x => hier.isSubclassOf(sootClass, Scene.v().getSootClass(x)))

  def isDialogFragment(sootClass: SootClass): Boolean =
    hier.isSubclassOf(sootClass, dialogFragmentClass)


  def isActivitySetContentViewWithInt(m: SootMethod): Boolean =
    m.getSubSignature == "void setContentView(int)" && isActivity(m.getDeclaringClass)

  def isActivitySetContentViewWithView(m: SootMethod): Boolean =
    m.getSubSignature == "void setContentView(android.view.View)" && isActivity(m.getDeclaringClass)

  def isActivityFindViewById(m: SootMethod): Boolean =
    m.getSubSignature == "android.view.View findViewById(int)" && isActivity(m.getDeclaringClass)

  def isActivityRunOnUiThread(m: SootMethod): Boolean =
    m.getSubSignature == "void runOnUiThread(java.lang.Runnable)" && isActivity(m.getDeclaringClass)

  def isDialogSetContentViewWithInt(m: SootMethod): Boolean =
    m.getSubSignature == "void setContentView(int)" && isDialogClass(m.getDeclaringClass)

  def isDialogSetContentViewWithView(m: SootMethod): Boolean =
    m.getSubSignature == "void setContentView(android.view.View)" && isDialogClass(m.getDeclaringClass)

  def isDialogFindViewById(m: SootMethod): Boolean =
    m.getSubSignature == "android.view.View findViewById(int)" && isDialogClass(m.getDeclaringClass)


  def getLifecycleMethodWindow(m: SootMethod): Option[SootClass] = {
    val cls = m.getDeclaringClass
    // FIXME: use a more precise heuristic
    if ((isActivity(cls) || isDialogClass(cls)) && m.getName.startsWith("on")) {
      Some(cls)
    } else {
      None
    }
  }
}
