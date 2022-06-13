/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import com.research.nomad.markii.{Core, Util}
import com.research.nomad.markii.analyses.PreVASCO
import io.github.izgzhen.msbase.{IOUtil, JsonUtil}
import soot.{Local, SootMethod, Value}
import soot.jimple.{AssignStmt, CastExpr, Constant, InstanceFieldRef, InstanceInvokeExpr, NewExpr, ParameterRef, ReturnStmt, StaticFieldRef, Stmt, ThisRef}
import soot.jimple.internal.{JIdentityStmt, JimpleLocal}
import vasco.{VascoContext, CustomAnalysis, ProgramRepresentation}

/**
 * TODO: implement AbstractValuePropVASCO with it
 * @param entryPoints entry-point methods
 * @tparam V Object abstract state
 */
class CustomStatePropVASCO[V <: AbsVal[V]](core: Core, preVasco: PreVASCO,
                                           entryPoints: List[SootMethod], transformer: CustomObjectStateTransformer[V])
  extends CustomAnalysis[SootMethod, soot.Unit, CustomDomain[V]] {
  type Domain = CustomDomain[V]
  type DomainContext = VascoContext[SootMethod, soot.Unit, Domain]

  private def logState(method: SootMethod, unit: soot.Unit, d: Domain): Unit = {
    if (!core.isDebugMode) return
    if (method.getSignature != "<com.example.validrec.Recorder: void startRecording(java.io.File)>" &&
        method.getSignature != "<com.example.validrec.MainActivity: void startRec(android.view.View)>" &&
        method.getSignature != "<com.example.validrec.MainActivity: void run_markii_generated()>") {
      return
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
    IOUtil.write(json, "/tmp/markii-custom-debug/" + method.getSignature + "@" + idx + ".json")
  }

  private val RETURN_LOCAL = new JimpleLocal("@return", null)

  def assigned(ctxMethod: SootMethod, stmt: Stmt, ref: Ref,
               value: Value, ctx: Domain, input: Domain, fromAliases: Map[Ref, Set[Ref]]): Domain = {
    val killed = input.killRef(ref)
    value match {
      case castExpr: CastExpr =>
        assigned(ctxMethod, stmt, ref, castExpr.getOp, ctx, input, fromAliases)
      case newExpr: NewExpr =>
        val sootClass = newExpr.getBaseType.getSootClass
        killed.newInstance(transformer, ref, sootClass, stmt)
      case rhsLocal: Local =>
        ctx.getAccessPath(rhsLocal) match {
          case Some(accessPath) =>
            var ret = killed
             for (r <- ref.fromAliases(fromAliases)) {
               ret = ret.withSubPath(r, accessPath)
             }
            ret
          case None =>
            if (rhsLocal.equivTo(RETURN_LOCAL)) {
              killed
            } else {
              killed.withAlias(ref, Ref.from(rhsLocal), fromAliases)
            }
        }
      case instanceFieldRef: InstanceFieldRef =>
        val rhsLocalRef = Ref.from(instanceFieldRef)
        input.getAccessPath(rhsLocalRef) match {
          case Some(accessPath) =>
            killed.withSubPath(ref, accessPath)
          case None => killed.withAlias(ref, rhsLocalRef, fromAliases)
        }
      case staticFieldRef: StaticFieldRef =>
        val rhsLocalRef = Ref.from(staticFieldRef)
        input.getAccessPath(rhsLocalRef) match {
          case Some(accessPath) =>
            killed.withSubPath(ref, accessPath)
          case None => killed
        }
      // TODO: currently not supported for simplicity
      case invokeExpr: InstanceInvokeExpr =>
        killed.invokeMethodAssign(transformer, ref, ctxMethod, invokeExpr, stmt)
      case parameterRef: ParameterRef =>
        val paramRef = Ref.ParamRef(parameterRef)
        ctx.getAccessPath(paramRef) match {
          case Some(accessPath) =>
            killed.withSubPath(ref, accessPath)
          case None => killed
        }
      case _ =>
        killed.assignWith(transformer, ref, stmt)
    }
  }

  override def normalFlowFunction(context: DomainContext, unit: soot.Unit, d: Domain): Domain = {
    logState(context.getMethod, unit, d)
    unit match {
      case assignStmt: AssignStmt =>
        val ref = Ref.from(assignStmt.getLeftOp)
        return assigned(context.getMethod, assignStmt, ref, assignStmt.getRightOp, d, d, d.getAliases)
      case stmt: JIdentityStmt =>
        return d.updateIdentity(transformer, context.getMethod, stmt)
      case retStmt: ReturnStmt =>
        return assigned(context.getMethod, retStmt, Ref.LocalRef(RETURN_LOCAL), retStmt.getOp, d, d, d.getAliases)
      case _ =>
    }
    d
  }

  override def callEntryFlowFunction(context: DomainContext, m: SootMethod,
                                     callSite: soot.Unit, d: Domain): Domain = {
    val stmt = callSite.asInstanceOf[Stmt]
    val invokeExpr = stmt.getInvokeExpr
    var ret = if (preVasco.isStartWindowStmt(callSite.asInstanceOf[Stmt])) {
      topValue()
    } else {
      d.getHeap
    }
    val globalAliases = d.getGlobalAliases
    if (m.hasActiveBody) {
      for (i <- 0 until invokeExpr.getArgCount) {
        ret = assigned(context.getMethod, stmt, Ref.LocalRef(m.getActiveBody.getParameterLocal(i)),
          invokeExpr.getArg(i), d, ret, globalAliases)
      }
      invokeExpr match {
        case instanceInvokeExpr: InstanceInvokeExpr =>
          ret = assigned(context.getMethod, stmt, Ref.LocalRef(m.getActiveBody.getThisLocal),
            instanceInvokeExpr.getBase, d, ret, globalAliases)
        case _ =>
      }
    }
    ret
  }

  // ???: How is the exit flow joined with the flow in the caller context? How is the caller context updated?
  override def callExitFlowFunction(context: DomainContext, m: SootMethod, unit: soot.Unit, d: Domain): Domain = {
    var ret = d.getHeap
    val globalAliases = d.getGlobalAliases
    // Process return value
    unit match {
      case assignStmt: AssignStmt =>
        ret = assigned(context.getMethod, assignStmt, Ref.LocalRef(assignStmt.getLeftOp.asInstanceOf[Local]),
          RETURN_LOCAL, d, ret, globalAliases)
      case _ =>
    }
    // Process this side-effect
    unit.asInstanceOf[Stmt].getInvokeExpr match {
      case instanceInvokeExpr: InstanceInvokeExpr =>
        val base = instanceInvokeExpr.getBase.asInstanceOf[Local]
        if (instanceInvokeExpr.getMethod.hasActiveBody) {
          val body = instanceInvokeExpr.getMethod.getActiveBody
          val thisLocal = body.getThisLocal
          ret = assigned(context.getMethod, unit.asInstanceOf[Stmt],
            Ref.LocalRef(base), thisLocal, d, ret, globalAliases)
        }
      case _ =>
    }
    val invokeExpr = unit.asInstanceOf[Stmt].getInvokeExpr
    // From paramMap map back the localMap
    for (i <- 0 until invokeExpr.getArgCount) {
      val toRef = invokeExpr.getArg(i)
      if (!toRef.isInstanceOf[Constant]) {
        ret = assigned(context.getMethod, unit.asInstanceOf[Stmt],
          Ref.from(toRef), m.getActiveBody.getParameterRefs.get(i), ctx = d, input = ret, d.getAliases)
      }
    }
    // TODO: Process global side-effect
    ret
  }

  override def callLocalFlowFunction(context: DomainContext, unit: soot.Unit, d: Domain): Domain = {
    logState(context.getMethod, unit, d)
    unit match {
      case assignStmt: AssignStmt =>
        val ref = Ref.from(assignStmt.getLeftOp)
        assigned(context.getMethod, assignStmt, ref, assignStmt.getRightOp, d, d, d.getAliases)
      case _ =>
        val stmt = unit.asInstanceOf[Stmt]
        if (stmt.containsInvokeExpr()) {
          if (!programRepresentation().resolveTargets(context.getMethod, unit).isEmpty) {
            return topValue()
          }
          d.invokeMethod(transformer, context.getMethod, stmt.getInvokeExpr, stmt)
        } else {
          d
        }
    }
  }

  override def boundaryValue(m: SootMethod): Domain = topValue()

  override def copy(d: Domain): Domain = d

  private val aftProgramRepresentation = new AFTProgramRepresentation(entryPoints)
  override def programRepresentation(): ProgramRepresentation[SootMethod, soot.Unit] =
    aftProgramRepresentation

  override def meet(d1: Domain, d2: Domain): Domain = d1.meet(d2)

  override def meetAssign(d1: Domain, d2: Domain): Domain = d1.meetAssignWith(d2)

  private val top: Domain = CustomDomain.makeTop[V]
  override def topValue(): Domain = top
}
