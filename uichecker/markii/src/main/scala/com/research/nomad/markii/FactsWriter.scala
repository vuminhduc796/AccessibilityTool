/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii

import org.apache.commons.text.StringEscapeUtils
import presto.android.gui.listener.EventType
import soot.SootClass
import soot.SootMethod
import java.io.BufferedWriter
import java.io.FileWriter
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Paths

import com.research.nomad.markii.dataflow.custom.AbsFS

import scala.collection.mutable

object FactsWriter {
  // FIXME (minor): Use sum type and reflection
  object Fact extends Enumeration {
    type Fact = Value
    val
      //----- View properties -----//
      idName,
      layoutHeight, layoutHeightDIP, layoutHeightSP,
      layoutWidth, layoutWidthDIP, layoutWidthSP,
      textSize, textSizeDIP, textSizeSP,
      background,
      viewClass,
      textContent,
      imageHasNoContentDescription,

      //----- Layout skeleton analysis -----//
      containsView,
      layout_constraintEnd_toStartOf, layout_constraintStart_toEndOf,
      layout_constraintEnd_toEndOf, layout_constraintStart_toStartOf,
      layout_constraintBottom_toTopOf, layout_constraintTop_toBottomOf,
      layout_constraintBottom_toBottomOf, layout_constraintTop_toTopOf,

      //----- Control-flow, life-cycle transition etc. -----//
      rootView, mainActivity,
      activityEventHandler,
      eventHandler,
      finishActivity,
      showDialog, // TODO: it needs to replace activityHandlerAllocDialog
      dismiss,
      intentFilter,
      methodLineNumber,

      startActivity,
      startViewActivityOfSomeHosts,
      startViewActivityOfMarketHost,

      //----- Value properties and Behaviors -----//
      buttonView, lifecycleMethod, preferenceActivity, dialogView,
      dialogViewButton,
      setStatus, setConsetInfoUpdateHandler, setNPA, readAudio, loadGoogleConsentForm,
      recordButton, loadWebViewUrl, adViewClass, serviceClass, adViewIdName,
      showSuspiciousAd, showSuspiciousInterstitialAd, invokesReflectiveAPI, serviceClassLastName,
      downloadApp, actionButton,
      showAd, showInterstitialAd,// FIXME: factor into reachable + ad API set?
      dialogTitle, dialogMessage,

      // For UnifiedObjectAPI
      enqueuedWorkRequest,

      // For custom state
      apiStateTransition
      = Value
  }
}

/**
 * Write facts in the input format for Souffle solver (https://souffle-lang.github.io/simple)
 *
 * @param factDir: Directory for facts. Created on initialization.
 */
class FactsWriter(val factDir: String) {
  private val writers = mutable.Map[String, BufferedWriter]()
  private val written = mutable.Set[(String, String)]()
  private val nameCounter = mutable.Map[String, Int]()

  Files.createDirectories(Paths.get(factDir))
  for (fact <- FactsWriter.Fact.values) {
    writers.put(fact.toString, new BufferedWriter(new FileWriter(factDir + "/" + fact.toString + ".facts")))
  }

  def getNameCounter: Map[String, Int] = nameCounter.toMap

  private val storedFacts = mutable.Map[FactsWriter.Fact.Value, mutable.ArrayBuffer[List[Any]]]()

  def getStoredFacts(fact: FactsWriter.Fact.Value): Iterable[List[Any]] =
    storedFacts.getOrElse(fact, Iterable.empty)

  def writeFact(fact: FactsWriter.Fact.Value, args: Any*): Unit = {
    storedFacts.getOrElseUpdate(fact, mutable.ArrayBuffer()).addOne(args.toList)
    writeFact_(fact, args: _*)
  }

  private def argToString(arg: Any): String =
    arg match {
      case null => "null"
      case _: Integer => arg.toString
      case method: SootMethod => StringEscapeUtils.escapeHtml4(method.getSignature)
      case clazz: SootClass => StringEscapeUtils.escapeHtml4(clazz.getName)
      case str: String => StringEscapeUtils.escapeHtml4(str)
      case AbsFS(Some(v)) => argToString(v)
      case eventType: EventType => eventType.name
      case _ => throw new RuntimeException("Write invalid arg " + arg + ": " + arg.getClass)
    }

  private def writeFact_(fact: FactsWriter.Fact.Value, args: Any*): Unit = {
    val builder = new StringBuilder
    var noTab = true
    for (arg <- args) {
      if (noTab) noTab = false
      else builder.append("\t")
      builder.append(argToString(arg))
    }
    builder.append("\n")
    val line = builder.toString
    val name = fact.toString
    if (!written.contains((name, line))) {
      written.add((name, line))
      try {
        val writer = getWriter(name)
        writer.write(line)
        writer.flush()
      }
      catch {
        case e: IOException =>
          e.printStackTrace()
          System.exit(-1)
      }
      if (!nameCounter.contains(name)) nameCounter.put(name, 0)
      nameCounter.put(name, nameCounter(name) + 1)
    }
  }

  def writeDimensionFact(fact: FactsWriter.Fact.Value, property: String, id: Int): Unit = {
    if (property.endsWith("dip")) {
      val dipIndex = property.indexOf("dip")
      val x = property.substring(0, dipIndex).toFloat
      writeFact(FactsWriter.Fact.withName(fact.toString + "DIP"), x.round, id)
      return
    }
    if (property.endsWith("sp")) {
      val spIndex = property.indexOf("sp")
      val x = property.substring(0, spIndex).toFloat
      writeFact(FactsWriter.Fact.withName(fact.toString + "SP"), x.round, id)
      return
    }
    writeFact(fact, property, id)
  }

  @throws[IOException]
  private def getWriter(name: String): BufferedWriter = {
    if (!writers.contains(name)) {
      writers.put(name, new BufferedWriter(new FileWriter(factDir + "/" + name + ".facts")))
    }
    writers(name)
  }

  @throws[IOException]
  def close(): Unit = {
    for (writer <- writers.values) {
      writer.close()
    }
  }
}
