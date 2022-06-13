/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

sealed abstract class AbstractValue extends Product with Serializable

object AbstractValue {
  // TODO: Improve intent analysis
  final case class Intent(intent: AbstractIntent) extends AbstractValue
}
