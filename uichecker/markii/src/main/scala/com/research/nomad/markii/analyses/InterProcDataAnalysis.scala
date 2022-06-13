package com.research.nomad.markii.analyses

import vasco.ProgramRepresentation

abstract class InterProcDataAnalysis[M, N, A] {
  def normalFlowFunction(contextMethod: M, node: N, inValue: A): A

  def callEntryFlowFunction(contextMethod: M, targetMethod: M, node: N, inValue: A): A

  def callExitFlowFunction(contextMethod: M, targetMethod: M, node: N, exitValue: A): A

  def callLocalFlowFunction(contextMethod: M, node: N, inValue: A): A

  def programRepresentation: ProgramRepresentation[M, N]

  def topValue: A

  def meet(op1: A, op2: A): A

  def boundaryValue(entryPoint: M): A

  def copy(src: A): A

  def onNewCall(method: M, invocation: N): Unit
}
