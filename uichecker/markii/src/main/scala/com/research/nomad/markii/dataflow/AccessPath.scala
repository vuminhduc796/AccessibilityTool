/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import scala.collection.mutable

/**
 * Finiteness is guaranteed by the individual implementations.
 * @tparam D Concrete type of abstract value
 */
trait AbsVal[D] {
  def meet(other: D): D
}

/**
 * Access path models an pointer with data and sub-fields
 *
 * Finiteness is guaranteed by the maxDepth cut-off
 *
 * @param data: Data associated with the current access-path
 * @param fields: fields to children access paths
 * @tparam D: Abstract data type
 */
case class AccessPath[D <: AbsVal[D]](data: Option[D],
                                      fields: Map[String, AccessPath[D]] = Map[String, AccessPath[D]](),
                                      maxDepth: Int = 3) {
  def merge(path: AccessPath[D]): AccessPath[D] = {
    val newData = (data, path.data) match {
      case (Some(s1), Some(s2)) => Some(s1.meet(s2))
      case (Some(s1), None) => Some(s1)
      case (None, Some(s2)) => Some(s2)
      case (None, None) => None
    }
    AccessPath[D](newData, AFTDomain.mergeMapOfAccessPath(fields, path.fields))
  }

  def updateData(f: (D, Option[Ref]) => D, ref: Option[Ref]): AccessPath[D] = {
    AccessPath(data = data.map(d => f(d, ref)), fields)
  }

  def traverse(): List[(List[String], D)] = {
    val m = mutable.Queue[(List[String], D)]()
    data match {
      case Some(ds) => m.addOne((List(), ds))
      case None =>
    }
    for ((fieldName, subPath) <- fields) {
      for ((path, ds) <- subPath.traverse()) {
        m.addOne((fieldName::path, ds))
      }
    }
    m.toList
  }

  override def toString: String = {
    traverse().map { case (path, ds) =>
      path.mkString(".") + ": " + ds.toString
    }.mkString("\n\t")
  }

  def toJSONObj: Object = {
    traverse().map { case (path, ds) =>
      (path.mkString("."), ds.toString)
    }
  }

  def truncatedFieldNames(fieldNames: List[String]): List[String] = {
    if (fieldNames.length > maxDepth) {
      fieldNames.slice(0, maxDepth) :+ "*"
    } else {
      fieldNames
    }
  }

  def kill(fieldNames: List[String]): AccessPath[D] = {
    truncatedFieldNames(fieldNames) match {
      case ::(head, next) => fields.get(head) match {
        case Some(subPath) => AccessPath(data = data, fields = fields + (head -> subPath.kill(next)))
        case None => this
      }
      case Nil => AccessPath(None, fields = fields)
    }
  }

  def get(fieldNames: List[String]): Option[AccessPath[D]] = {
    truncatedFieldNames(fieldNames) match {
      case ::(head, next) => fields.get(head) match {
        case Some(subPath) => subPath.get(next)
        case None => None
      }
      case Nil => Some(this)
    }
  }

  /**
   *
   * @param fieldNames
   * @param valMapper
   * @param ref -- identify the updated program value
   * @return
   */
  def updateData(fieldNames: List[String], valMapper: (D, Option[Ref]) => D, ref: Option[Ref] = None): AccessPath[D] = {
    truncatedFieldNames(fieldNames) match {
      case ::(head, next) => fields.get(head) match {
        case Some(subPath) => AccessPath(data, fields + (head -> subPath.updateData(next, valMapper, ref)))
        case None => this
      }
      case Nil => this.updateData(valMapper, ref)
    }
  }

  /**
   * Get all data in sub-fields of this access path
   * @return
   */
  def getAllFieldsData: Option[D] = {
    val allData = fields.values.map(_.getAllData).toList
    allData.fold(None) {
      case (Some(d1), Some(d2)) => Some(d1.meet(d2))
      case (Some(d1), _) => Some(d1)
      case (_, Some(d2)) => Some(d2)
      case _ => None
    }
  }
  /**
   * Get all data in current and sub-fields of this access path
   * @return
   */
  def getAllData: Option[D] = {
    val allData = data :: fields.values.map(_.getAllData).toList
    allData.fold(None) {
      case (Some(d1), Some(d2)) => Some(d1.meet(d2))
      case (Some(d1), _) => Some(d1)
      case (_, Some(d2)) => Some(d2)
      case _ => None
    }
  }

  def truncated(d: Int): AccessPath[D] = {
    if (d == 0)
      if (fields.nonEmpty) {
        getAllFieldsData match {
          case Some(fieldsD) =>
            AccessPath(data = data).add(List("*"), fieldsD)
          case None =>
            AccessPath(data = data)
        }
      } else {
        this
    } else {
      AccessPath(data = data, fields = fields.map { case (k, v) => (k, v.truncated(d - 1))})
    }
  }

  def add(fieldNames: List[String], subPath: AccessPath[D]): AccessPath[D] = {
    val truncated = truncatedFieldNames(fieldNames)
    val leftDepth = maxDepth - truncated.size
    val subPathTruncated = subPath.truncated(leftDepth)
    truncated match {
      case ::(head, next) => fields.get(head) match {
        case Some(accessPath) => AccessPath(data = data, fields = fields + (head -> accessPath.add(next, subPathTruncated)))
        case None => AccessPath(data = data, fields = fields + (head -> AccessPath(None).add(next, subPathTruncated)))
      }
      case Nil => merge(subPathTruncated)
    }
  }

  def add(fieldNames: List[String], newData: D): AccessPath[D] = {
    truncatedFieldNames(fieldNames) match {
      case ::(head, next) => fields.get(head) match {
        case Some(subPath) => AccessPath(data = data, fields = fields + (head -> subPath.add(next, newData)))
        case None => AccessPath(data = data, fields = fields + (head -> AccessPath(None).add(next, newData)))
      }
      case Nil =>
        val newData2 = data match {
          case Some(d) => d.meet(newData)
          case None => newData
        }
        AccessPath(data = Some(newData2), fields = fields)
    }
  }
}
