package com.research.nomad.markii.analyses

import soot.toolkits.graph.DirectedGraph

case class AnalyzedMethod[A](var entryValue: A, var exitValue: Option[A] = None)

case class WorkListItem[M, N](method: M, unit: N, cfg: DirectedGraph[N])

case class WorkListItemM[M, N](method: M, cfg: DirectedGraph[N])

case class CallSite[M, N](method: M, unit: N, cfg: DirectedGraph[N]) {
  override def equals(obj: Any): Boolean = {
    if (obj == null) {
      return false
    } else if (getClass != obj.getClass) {
      return false
    }
    val other = obj.asInstanceOf[CallSite[M, N]]
    other.unit.equals(unit) && other.method.equals(method)
  }

  override def hashCode(): Int = {
    val prime = 31
    var result = 1
    result = prime * result + unit.hashCode()
    result = prime * result + method.hashCode()
    result
  }
}