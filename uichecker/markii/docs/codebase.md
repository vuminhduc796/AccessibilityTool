# Codebase

The current codebase is a mixture of Scala and Java. The Java part is mostly from [GATOR](http://web.cse.ohio-state.edu/presto/software/gator/), which provides [Soot](https://github.com/Sable/soot/) harness and some other
supporting code. The main analysis is written in Scala, inside [this directory](https://github.com/izgzhen/ui-checker/tree/master/markii/src/main/scala/com/research/nomad/markii).

The analysis code's entry is at [`Core.run`](https://github.com/izgzhen/ui-checker/blob/75f015c1d5192a46afc7c82b91a5492fe0731056/markii/src/main/scala/com/research/nomad/markii/Core.scala#L904),
which is hooked into the GATOR provided harness.

The inputs & outputs arguments are specified by client params (see `Core.readConfigs`), and all outputs are written to
files.

The information from analyses are processed later inside other methods of `Core` and emitted to
Datalog `.facts` format.

## Control flow graph (CFG)

The interprocedural-CFG (iCFG) is available to use inside the `def run`:
See [this line](https://github.com/izgzhen/markii/blob/c017ee31ecc8165d297dbf15194f0d836011b2b0/src/main/scala/com/research/nomad/markii/Core.scala#L350) as an example.

## Pointer-related

- [`def isAlias`](https://github.com/izgzhen/markii/blob/c017ee31ecc8165d297dbf15194f0d836011b2b0/src/main/scala/com/research/nomad/markii/Core.scala#L191): Decide whether two points are aliases

## GUI analysis

- [analysis](https://github.com/izgzhen/ui-checker/blob/master/markii/src/main/scala/com/research/nomad/markii/dataflow/AbstractValuePropVasco.scala)

Most GUI API semantics are encoded in the VASCO part. Essentially, it implements a data-flow analysis that
propagate an abstract state [`AFTDomain`](https://github.com/izgzhen/ui-checker/blob/master/markii/src/main/scala/com/research/nomad/markii/dataflow/AFTDomain.scala), which models
the most essential information about GUI.

Based on VASCO.

## Misc analyses

- IC3-based intent analysis: run separately and MarkII will use its output. MarkII also has a fallback implementation.

## FAQ

**What does entrypoint mean?**

Entrypoint is the statement from which the data-flow propagation begins. See https://en.wikipedia.org/wiki/Entry_point.

**How do i turn on the debug mode?**

See https://github.com/izgzhen/markii/wiki/Developer-Guide#dumped-debugging-info

**Should VASCO analyze the methods inside an inner class?**

Yes, and static anlayzer treats inner or normal class all the same.

**Difference between entrypoints and endpoints?**

Endpoints are the statements at which a method exits. For example,

```python
def f(a):
  if a > 1:
     return True    # exit point 1
  else:
     return False   # exit point 2
```

**How is iCFG generated?**

First, iCFG is the combination of call-graph and control-flow graph.

For IFDS/Heros, it is like here: https://github.com/izgzhen/markii/blob/d0d3f7c1562df62f8f882391e92bd9627c0c14f4/src/main/scala/com/research/nomad/markii/Core.scala#L302.

For VASCO, it is using a more dynamic approach: https://github.com/izgzhen/markii/blob/26da0655ae612cfce56a1aee72e09ad5be8ca7aa/src/main/scala/com/research/nomad/markii/dataflow/AFTProgramRepresentation.scala#L23 (`resolveTargets` tells you which methods might be called at a call-site)

Underlying both of them is the same call-graph analysis result from e.g. Spark algorithm.

**Why is some method not analyzed by data-flow analysis?**

The data-flow analysis (e.g. VASCO) propagates information in an inter-procedural control flow graph (iCFG),
starting from entrypoints. There might be two reasons for a method not processed by the analysis:

1. The method is not in call graph at all. You should first confirm whether the method is in call graph after pre-analysis by either:
  * Setting debugging breakpoint at e.g. `https://github.com/izgzhen/markii/blob/d0d3f7c1562df62f8f882391e92bd9627c0c14f4/src/main/scala/com/research/nomad/markii/Core.scala#L50` and check `Scene.v().getCallGraph()`. 
  * Or find it in the dumped call-graph (https://github.com/izgzhen/markii/wiki/Developer-Guide#dumped-debugging-info)
2. The method is not reachable from entrypoints. The reasons are pretty complicated...please submit an issue on the details of your problem.