/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import soot.{Local, SootClass, Value}
import soot.jimple.{ArrayRef, InstanceFieldRef, ParameterRef, StaticFieldRef}

import scala.collection.mutable

sealed abstract class Ref extends Product with Serializable {
  def field(name: String): Ref
  def fields(names: List[String]): Ref

  /**
   * TODO: should it also include this ref?
   * @param aliases
   * @return
   */
  def fromAliases(aliases: Map[Ref, Set[Ref]]): Set[Ref]
}

object Ref {
  final case class GlobalRef(cls: SootClass, fields: List[String] = List()) extends Ref {
    def field(name: String): Ref = GlobalRef(cls, fields ++ List(name))
    def fields(names: List[String]): Ref = GlobalRef(cls, fields ++ names)

    def fromAliases(aliases: Map[Ref, Set[Ref]]): Set[Ref] = {
      if (fields.isEmpty) {
        return aliases.getOrElse(this, Set(this))
      }
      val ret = mutable.Set[Ref]()
      for (i <- fields.indices) {
        val (left, right) = fields.splitAt(i)
        for (leftAlias <- aliases.getOrElse(GlobalRef(cls, left), Set(GlobalRef(cls, left)))) {
          ret.add(leftAlias.fields(right))
        }
      }
      ret.toSet
    }

    override def toString: String = {
      (cls.getName :: fields).mkString(".")
    }
  }

  final case class ParamRef(parameterRef: ParameterRef, fields: List[String] = List()) extends Ref {
    def field(name: String): Ref = ParamRef(parameterRef, fields ++ List(name))
    def fields(names: List[String]): Ref = ParamRef(parameterRef, fields ++ names)

    def fromAliases(aliases: Map[Ref, Set[Ref]]): Set[Ref] = {
      if (fields.isEmpty) {
        return aliases.getOrElse(this, Set(this))
      }
      val ret = mutable.Set[Ref]()
      for (i <- fields.indices) {
        val (left, right) = fields.splitAt(i)
        for (leftAlias <- aliases.getOrElse(ParamRef(parameterRef, left), Set(ParamRef(parameterRef, left)))) {
          ret.add(leftAlias.fields(right))
        }
      }
      ret.toSet
    }

    override def toString: String = {
      (parameterRef.toString :: fields).mkString(".")
    }
  }

  final case class LocalRef(local: Local, fields: List[String] = List()) extends Ref {
    def field(name: String): Ref = LocalRef(local, fields ++ List(name))
    def fields(names: List[String]): Ref = LocalRef(local, fields ++ names)

    def fromAliases(aliases: Map[Ref, Set[Ref]]): Set[Ref] = {
      if (fields.isEmpty) {
        return aliases.getOrElse(this, Set(this))
      }
      val ret = mutable.Set[Ref]()
      for (i <- fields.indices) {
        val (left, right) = fields.splitAt(i)
        for (leftAlias <- aliases.getOrElse(LocalRef(local, left), Set(LocalRef(local, left)))) {
          ret.add(leftAlias.fields(right))
        }
      }
      ret.toSet
    }

    override def toString: String = {
      (local.getName :: fields).mkString(".")
    }
  }

  def from(l: Local): Ref = LocalRef(l)

  def from(instanceFieldRef: InstanceFieldRef): Ref = {
    val localRef = from(instanceFieldRef.getBase.asInstanceOf[Local])
    localRef.field(instanceFieldRef.getField.getName)
  }

  def from(staticFieldRef: StaticFieldRef): Ref = {
    val ref = GlobalRef(staticFieldRef.getFieldRef.declaringClass())
    ref.field(staticFieldRef.getField.getName)
  }

  @scala.annotation.tailrec
  def from(value: Value): Ref = {
    value match {
      case parameterRef: ParameterRef => ParamRef(parameterRef)
      case staticFieldRef: StaticFieldRef => from(staticFieldRef)
      case local: Local => from(local)
      case instanceFieldRef: InstanceFieldRef => from(instanceFieldRef)
      case arrayRef: ArrayRef => from(arrayRef.getBase)
    }
  }
}
