package com.research.nomad.markii.analyses

import com.research.nomad.markii.Core
import com.research.nomad.markii.dataflow.{AFTDomain, AbstractValuePropVASCO}
import soot.SootMethod
import vasco.{ForwardInterProceduralAnalysis, ProgramRepresentation, VascoContext}

import scala.jdk.CollectionConverters._

case class ContextSensitiveAnalysisImpl(core: Core, preVasco: PreVASCO, entryPoints: List[SootMethod],
                                        analysis: ForwardInterProceduralAnalysis[SootMethod, soot.Unit, AFTDomain])
  extends AbstractValuePropVASCO(core, preVasco, entryPoints) {

  override def onNewCall(method: SootMethod, invocation: soot.Unit): Unit = {
    for (ctx <- analysis.getContexts(method).asScala) {
      ctx.setValueBefore(invocation, topValue())
      ctx.setValueAfter(invocation, topValue())
    }
    analysis.initContext(method, topValue())
  }
}

case class ContextSensitiveAnalysis(core: Core, preVasco: PreVASCO, entryPoints: List[SootMethod])
  extends ForwardInterProceduralAnalysis[SootMethod, soot.Unit, AFTDomain] {
  val impl = ContextSensitiveAnalysisImpl(core, preVasco, entryPoints, this)

  type DomainContext = VascoContext[SootMethod, soot.Unit, impl.Domain]

  override def normalFlowFunction(context: DomainContext, node: soot.Unit, inValue: impl.Domain): impl.Domain =
    impl.normalFlowFunction(context.getMethod, node, inValue)

  override def callEntryFlowFunction(context: DomainContext,
                                     targetMethod: SootMethod,
                                     node: soot.Unit, inValue: impl.Domain): impl.Domain =
    impl.callEntryFlowFunction(context.getMethod, targetMethod, node, inValue)

  override def callExitFlowFunction(context: DomainContext, targetMethod: SootMethod,
                                    node: soot.Unit, exitValue: impl.Domain): impl.Domain =
    impl.callExitFlowFunction(context.getMethod, targetMethod, node, exitValue)

  override def callLocalFlowFunction(context: DomainContext, node: soot.Unit, inValue: impl.Domain): impl.Domain =
    impl.callLocalFlowFunction(context.getMethod, node, inValue)

  override def boundaryValue(entryPoint: SootMethod): AFTDomain = impl.boundaryValue(entryPoint)

  override def copy(src: AFTDomain): AFTDomain = impl.copy(src)

  override def meet(op1: AFTDomain, op2: AFTDomain): AFTDomain = impl.meet(op1, op2)

  override def programRepresentation(): ProgramRepresentation[SootMethod, soot.Unit] = impl.programRepresentation()

  override def topValue(): AFTDomain = impl.topValue()
}
