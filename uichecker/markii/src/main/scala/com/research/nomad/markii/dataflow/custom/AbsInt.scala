/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow.custom

import com.research.nomad.markii.dataflow.{AbsVal, CustomDomain, CustomObjectStateTransformer}
import soot.jimple.{AssignStmt, IntConstant, Stmt}

sealed abstract class AbsIntVal extends Product with Serializable with AbsVal[AbsIntVal]

object AbsIntVal {
  def from(value: Int): AbsIntVal = Interval(value, value + 1)

  final case class Interval(lower: Int, upper: Int) extends AbsIntVal {
    override def meet(other: AbsIntVal): AbsIntVal = {
      other match {
        case Interval(l, u) => Interval(lower.min(l), upper.max(u))
        case Arbitrary() => Arbitrary()
      }
    }
  }

  /**
   * Arbitrary value
   */
  final case class Arbitrary() extends AbsIntVal {
    override def meet(other: AbsIntVal): AbsIntVal = Arbitrary()
  }
}

object AbsInt extends CustomObjectStateTransformer[AbsIntVal] {
  override def fromAssign(ctx: CustomDomain[AbsIntVal], stmt: Stmt): Option[AbsIntVal] = {
    stmt match {
      case assignStmt: AssignStmt =>
        assignStmt.getRightOp match {
          case intConstant: IntConstant => Some(AbsIntVal.from(intConstant.value))
          case _ => None
        }
      case _ => None
    }
  }
}
