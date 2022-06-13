/*
 * Copyright (c) 2020. Zhen Zhang
 */

package com.research.nomad.markii.dataflow

import com.research.nomad.markii.{Constants, PreAnalyses}
import soot.jimple.internal.JIdentityStmt
import soot.jimple.{InstanceInvokeExpr, InvokeExpr, ParameterRef, Stmt, ThisRef}
import soot.{Local, RefType, SootClass, SootMethod}

trait CustomObjectStateTransformer[S <: AbsVal[S]] {
  def initInstance(sootClass: SootClass): Option[S] = None
  def fromAssign(ctx: CustomDomain[S], stmt: Stmt): Option[S] = None
  def updatedInstance(prev: S, instanceInvokeExpr: InstanceInvokeExpr, callSite: Stmt, ref: Option[Ref]): S = prev
  def returnFromInstanceInvoke(s: S, invokeExpr: InvokeExpr): Option[S] = None
  def returnFromInvoke(invokeExpr: InvokeExpr): Option[S] = None
}

/**
 * TODO
 */
case class CustomDomain[S <: AbsVal[S]](private val localMap: Map[Local, AccessPath[S]],
                                        private val paramMap: Map[ParameterRef, AccessPath[S]],
                                        private val globalMap: Map[SootClass, AccessPath[S]],
                                        private val aliases: Map[Ref, Set[Ref]]) {
  /**
   * STRUCTURAL METHOD
   */
  def meet(d: CustomDomain[S]): CustomDomain[S] = {
    if (equalsTop) return d
    if (d.equalsTop) return this
    if (equals(d)) return this
    CustomDomain(
      CustomDomain.mergeMapOfAccessPath(localMap, d.localMap),
      CustomDomain.mergeMapOfAccessPath(paramMap, d.paramMap),
      CustomDomain.mergeMapOfAccessPath(globalMap, d.globalMap),
      CustomDomain.mergeMapOfSets(aliases, d.aliases))
  }

  def meetAssignWith(d: CustomDomain[S]): CustomDomain[S] = {
    if (equalsTop) return d
    if (d.equalsTop) return this
    if (equals(d)) return this
    CustomDomain(
      CustomDomain.mergeFromRightMapOfAccessPath(localMap, d.localMap),
      CustomDomain.mergeFromRightMapOfAccessPath(paramMap, d.paramMap),
      CustomDomain.mergeFromRightMapOfAccessPath(globalMap, d.globalMap),
      aliases
    )
  }

  def equalsTop: Boolean = localMap.isEmpty && paramMap.isEmpty && globalMap.isEmpty && aliases.isEmpty

  /**
   * STRUCTURAL METHOD
   */
  def updateVal(contextMethod: SootMethod, stmt: Stmt, local: Local,
                valMapper: (S, Option[Ref]) => S): CustomDomain[S] = {
    val globalRefs = Ref.from(local).fromAliases(getGlobalAliases).collect {
      case globalRef: Ref.GlobalRef => globalRef
    }
    val paramRefs = Ref.from(local).fromAliases(getParamAliases).collect {
      case paramRef: Ref.ParamRef=> paramRef
    }
    copy(localMap = localMap.map { case (l, accessPath) =>
      if (PreAnalyses.isAlias(local, l, stmt, stmt, contextMethod)) {
        (l, accessPath.updateData(valMapper, None)) // FIXME: support local identifier
      } else {
        (l, accessPath)
      }
    }, paramMap = paramMap.map { case (parameterRef, accessPath) =>
      var ret = accessPath
      for (paramRef <- paramRefs) {
        if (paramRef.parameterRef.equivTo(parameterRef)) {
          ret = ret.updateData(paramRef.fields, valMapper)
        }
      }
      (parameterRef, ret)
    }, globalMap = globalMap.map { case (cls, accessPath) =>
      var ret = accessPath
      for (globalRef <- globalRefs) {
        if (globalRef.cls == cls) {
          ret = ret.updateData(globalRef.fields, valMapper, Some(globalRef))
        }
      }
      (cls, ret)
    })
  }

  def updateIdentity(transformer: CustomObjectStateTransformer[S],
                     ctxMethodL: SootMethod, stmt: JIdentityStmt): CustomDomain[S] = {
    val methodClass = ctxMethodL.getDeclaringClass
    val localRef = Ref.from(stmt.getLeftOp)
    stmt.getRightOp match {
      case parameterRef: ParameterRef =>
        return withAlias(localRef, Ref.from(parameterRef), aliases)
      case _ =>
    }
    this
  }

  def withAlias(ref: Ref, rhsRef: Ref, fromAliases: Map[Ref, Set[Ref]] = aliases): CustomDomain[S] = {
    val rhsRefs = rhsRef.fromAliases(fromAliases)
    val newAliases = aliases.getOrElse(ref, Set()) ++ rhsRefs
    copy(
      aliases = aliases + (ref -> newAliases)
    )
  }

  /**
   * STRUCTURAL METHOD
   */
  def sizeSummary: Map[String, Int] =
    Map(
      "localMap" -> localMap.size,
      "globalMap" -> globalMap.size,
      "paramMap" -> paramMap.size,
      "aliases" -> aliases.size
    )

  /**
   * STRUCTURAL METHOD
   */
  def getHeap: CustomDomain[S] = copy(localMap = Map(), aliases = Map(), paramMap = Map())

  def getAliases: Map[Ref, Set[Ref]] = aliases

  def getGlobalAliases: Map[Ref, Set[Ref]] = {
    aliases.map {
      case (ref, refAliases) => (ref, refAliases.filter(_.isInstanceOf[Ref.GlobalRef]) )
    } filter(_._2.nonEmpty)
  }

  def getParamAliases: Map[Ref, Set[Ref]] = {
    aliases.map {
      case (ref, refAliases) => (ref, refAliases.filter(_.isInstanceOf[Ref.ParamRef]) )
    } filter(_._2.nonEmpty)
  }

  /**
   * STRUCTURAL METHOD
   */
  def nonEmpty: Boolean =
    localMap.nonEmpty || globalMap.nonEmpty

  def newInstance(transformer: CustomObjectStateTransformer[S], ref: Ref,
                  sootClass: SootClass, stmt: Stmt): CustomDomain[S] = {
    transformer.initInstance(sootClass) match {
      case Some(v) => withVal(ref, v)
      case None => this
    }
  }

  def invokeMethod(transformer: CustomObjectStateTransformer[S], ctxMethod: SootMethod,
                   invokeExpr: InvokeExpr, stmt: Stmt): CustomDomain[S] = {
    invokeExpr match {
      case instanceInvokeExpr: InstanceInvokeExpr =>
        updateVal(ctxMethod, stmt, instanceInvokeExpr.getBase.asInstanceOf[Local],
          (v, ref) => transformer.updatedInstance(v, instanceInvokeExpr, stmt, ref))
      case _ => this
    }
  }

  def assignWith(transformer: CustomObjectStateTransformer[S], ref: Ref, stmt: Stmt): CustomDomain[S] = {
    transformer.fromAssign(this, stmt) match {
      case Some(value) =>
        var ret = this
        for (r <- ref.fromAliases(aliases)) {
          ret = ret.withVal(r, value)
        }
        ret.withVal(ref, value)
      case None => this
    }
  }

    def invokeMethodAssign(transformer: CustomObjectStateTransformer[S], ref: Ref, ctxMethod: SootMethod,
                         invokeExpr: InvokeExpr, stmt: Stmt): CustomDomain[S] = {
    invokeExpr match {
      case instanceInvokeExpr: InstanceInvokeExpr =>
        var ret = this
        for (v <- getLocalVals(ctxMethod, stmt, instanceInvokeExpr.getBase.asInstanceOf[Local])) {
          transformer.returnFromInstanceInvoke(v, invokeExpr) match {
            case Some(value) => ret = ret.withVal(ref, value)
            case None =>
          }
        }
        if (invokeExpr.getMethod.getSignature == "<android.app.Activity: android.app.Application getApplication()>") {
          val activityClass = invokeExpr.asInstanceOf[InstanceInvokeExpr].getBase.getType.asInstanceOf[RefType].getSootClass
          ret = ret.withAlias(ref, Ref.GlobalRef(activityClass, List("__app")))
        } else {
          transformer.returnFromInvoke(invokeExpr) match {
            case Some(value) => ret = ret.withVal(ref, value)
            case None =>
          }
        }
        ret
      case _ => this
    }
  }

  /**
   * STRUCTURAL METHOD
   */
  private def equivTo(domain: CustomDomain[S]): Boolean =
    localMap == domain.localMap && globalMap == domain.globalMap

  override def equals(obj: Any): Boolean = {
    if (obj == null) return false
    if (super.equals(obj)) return true
    obj match {
      case domain: CustomDomain[S] =>
        if (hashCode() == domain.hashCode()) {
          equivTo(domain)
        } else {
          false
        }
      case _ => false
    }
  }

  override def toString: String = sizeSummary.toString

  def getLocalVals(contextMethod: SootMethod, stmt: Stmt, local: Local): Iterable[S] = {
    localMap.flatMap { case (l, accessPath) =>
      if (PreAnalyses.isAlias(local, l, stmt, stmt, contextMethod)) {
        accessPath.data match {
          case Some(value) => Set(value)
          case None => None
        }
      } else {
        Set()
      }
    }
  }

  def getAccessPath(l: Local): Option[AccessPath[S]] = localMap.get(l)

  def getAccessPath(ref: Ref): Option[AccessPath[S]] =
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        globalMap.get(cls) match {
          case Some(accessPath) => accessPath.get(fields)
          case None => None
        }
      case Ref.ParamRef(cls, fields) =>
        paramMap.get(cls) match {
          case Some(accessPath) => accessPath.get(fields)
          case None => None
        }
      case Ref.LocalRef(local, fields) =>
        localMap.get(local) match {
          case Some(accessPath) => accessPath.get(fields)
          case None => None
        }
    }

  def withSubPath(ref: Ref, subPath: AccessPath[S]): CustomDomain[S] = {
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        copy(
          globalMap = globalMap.get(cls) match {
            case None => globalMap + (cls -> AccessPath[S](None).add(fields, subPath))
            case Some(accessPath) => globalMap + (cls -> accessPath.add(fields, subPath))
          }
        )
      case Ref.ParamRef(cls, fields) =>
        copy(
          paramMap = paramMap.get(cls) match {
            case None => paramMap + (cls -> AccessPath(None).add(fields, subPath))
            case Some(accessPath) => paramMap + (cls -> accessPath.add(fields, subPath))
          }
        )
      case Ref.LocalRef(local, fields) =>
        copy(
          localMap = localMap.get(local) match {
            case None => localMap + (local -> AccessPath(None).add(fields, subPath))
            case Some(accessPath) => localMap + (local -> accessPath.add(fields, subPath))
          }
        )
    }
  }

  def killRef(ref: Ref): CustomDomain[S] =
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        copy(globalMap = (fields, globalMap.get(cls)) match {
          case (_, None) => globalMap
          case (List(), _) => globalMap - cls
          case (fields, Some(accessPath)) => globalMap + (cls -> accessPath.kill(fields))
        })
      case Ref.ParamRef(cls, fields) =>
        copy(paramMap = (fields, paramMap.get(cls)) match {
          case (_, None) => paramMap
          case (List(), _) => paramMap - cls
          case (fields, Some(accessPath)) => paramMap + (cls -> accessPath.kill(fields))
        })
      case Ref.LocalRef(local, fields) =>
        copy(localMap = (fields, localMap.get(local)) match {
          case (_, None) => localMap
          case (List(), _) => localMap - local
          case (fields, Some(accessPath)) => localMap + (local -> accessPath.kill(fields))
        })
    }

  def withVal(ref: Ref, v: S): CustomDomain[S] = {
    ref match {
      case Ref.GlobalRef(cls, fields) =>
        copy(
          globalMap = globalMap + (cls -> AccessPath(None).add(fields, v))
        )
      case Ref.LocalRef(local, fields) =>
        copy(
          localMap = localMap + (local -> AccessPath(None).add(fields, v))
        )
      case Ref.ParamRef(p, fields) =>
        copy(
          paramMap = paramMap + (p -> AccessPath(None).add(fields, v))
        )
    }
  }

  def toJSONObj: Object = Map[String, Object](
    "localMap" -> localMap.map { case (k, v) => (k.toString(), v.toJSONObj) },
    "globalMap" -> globalMap.map { case (k, v) => (k.toString, v.toJSONObj) },
    "aliases" -> aliases.map { case (k, v) => (k.toString, v.mkString(", ")) }
  )
}

object CustomDomain {
  def makeTop[V <: AbsVal[V]]: CustomDomain[V] = CustomDomain[V](Map(), Map(), Map(), Map())

  def mapToString[K, V](m: Map[K, V]): String =
    m.map { case (k, v) => "\t " + k + " -> " + v }.mkString("\n")

  def mergeMapOfSets[K, V](m1: Map[K, Set[V]], m2: Map[K, Set[V]]): Map[K, Set[V]] = {
    if (m1.equals(m2)) return m1
    mergeMaps(m1, m2, (m1: Set[V], m2: Set[V]) => m1 ++ m2)
  }

  def mergeMaps[K, V](m1: Map[K, V], m2: Map[K, V], f: (V, V) => V): Map[K, V] = {
    (m1.keySet ++ m2.keySet).map(k => {
      if (m1.contains(k) && m2.contains(k)) {
        (k, f(m1(k), m2(k)))
      } else if (m1.contains(k)) {
        (k, m1(k))
      } else {
        (k, m2(k))
      }
    }).toMap
  }

  def mergeFromRightMaps[K, V](m1: Map[K, V], m2: Map[K, V]): Map[K, V] = {
    (m1.keySet ++ m2.keySet).map(k => {
      if (m2.contains(k)) {
        (k, m2(k))
      } else {
        (k, m1(k))
      }
    }).toMap
  }

  def mergeMapOfAccessPath[K, D <: AbsVal[D]](m1: Map[K, AccessPath[D]],
                                 m2: Map[K, AccessPath[D]]): Map[K, AccessPath[D]] = {
    if (m1.equals(m2)) return m1
    mergeMaps(m1, m2, (m1: AccessPath[D], m2: AccessPath[D]) => m1.merge(m2))
  }

  def mergeFromRightMapOfAccessPath[K, D <: AbsVal[D]](m1: Map[K, AccessPath[D]],
                                                       m2: Map[K, AccessPath[D]]): Map[K, AccessPath[D]] = {
    if (m1.equals(m2)) return m1
    mergeFromRightMaps(m1, m2)
  }
}