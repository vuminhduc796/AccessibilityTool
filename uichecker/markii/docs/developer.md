# Developer Guide

- The recommended IDE: IntelliJ IDEA

## Basic Setup in IntelliJ IDEA

Most of the time it should work out of the box...it is supposed to be intelli-gent, right? But if not, e.g. syntax highlighting is problematic, check the following possibilities:

- Have you installed the latest Scala plugin?
    * You need to install Scala plugin BEFORE import/open this project. You should expect to [see SBT panel](https://www.dropbox.com/s/i72yom7ef31w8oz/sbt-panel.png?dl=0).
- Are both scala and java part of the project's source folders? (e.g. you should see something like [this](https://www.dropbox.com/s/4ynh0i4r361oqpb/markii-project-structure-source-folder.png?dl=0) in Project Structure)

Other troubles:

* Build ERROR: `Error:java: invalid source release: 11`:  Run `clean` inside "sbt shell". Normally you will get this error after fixing the project SDK from 11 to 8...


## Debugging

### Debug in IntelliJ

The first step is to create an IntelliJ run configuration (e.g. like [this](https://www.dropbox.com/s/x8zctgl51tbwxzh/intellij-markii-run-config.png?dl=0)). To set the "Program arguments", you can run the markii first:
```
./build-run-markii.sh tests/validrec/app-debug.apk tests/validrec.facts
......
...... java -Xmx12G -cp /Users/zhen/projects/android-ui-research/android-ui-checker/markii/target/scala-2.13/markii-assembly-0.1.jar presto.android.Main -configDir ... ... -clientParam output:... -enableStringPropertyAnalysis
# Ctrl-C to stop the command as soon as the above debugging info appears
```

NOTE: You need to stop early to preserve the temporary unpacked APK in the step before the one we care about.

Using the printed our command, we take its part after `java -Xmx12G -cp  .../markii-assembly-0.1.jar presto.android.Main`, which are
the actual program argument.

### Dumped debugging info

Adding environment variable `DEBUG=1` turns on debugging mode, and the program will dump the following extra things:

- call graph: `/tmp/call-graph.txt`
- captured abstract state in data-flow propagation: `/tmp/{ifds,vasco}-abstractions.txt`. See `com.research.nomad.markii.dataflow.AbstractValuePropVASCO#logState` for more details.
- logged state of analyzer: `/tmp/markii-custom-debug` and `/tmp/markii-debug` (useful if the analysis is slow/stuck)
    + Use `python tools/debug-markii.py custom` to pretty-print `/tmp/markii-custom-debug`
    + Use `python tools/debug-markii.py` to pretty-print `/tmp/markii-debug`


## Tests

- Unit tests
  + Run: `sbt test`
  + Implementation: `src/test/scala/com/research/nomad/markii`
- Regression tests
  + Run: `make test-all`
  + Update regression tests' stored outputs: `make record-all`

## Debugging performance issue

- Run with "CPU Profiling" in IDEA
- Investigate: Are all analysis necessary?

### Performance analysis

Main stages:

* Pre-analysis
* MarkII IFDS analysis
* MarkII VASCO analysis

Many related statistics are recorded at `$OUTPUT_DIR/report.yaml` (works in both debug and non-debug mode, and it is
updated even if the program exits half-way).

## Libraries & Papers

- VASCO https://github.com/rohanpadhye/vasco
  + Paper https://dl.acm.org/doi/10.1145/2487568.2487569, or https://arxiv.org/abs/1304.6274
  
## Update dependency

### Soot

Current version: [4.2.1](https://github.com/soot-oss/soot/tree/4.2.1).

TODO: instructions of mirroring its source tree.

### FlowDroid

Current version: [v2.8](https://github.com/secure-software-engineering/FlowDroid/tree/v2.8).

Mirroring its source tree:

1. Clone the repo to `$FLOWDROID_REPO`, check out v2.8 inside it, go back to this repo
2. `cp -r ../FlowDroid/soot-infoflow/src/soot/jimple/infoflow/* src/main/java/soot/jimple/infoflow/`
3. `cp -r ../FlowDroid/soot-infoflow-android/src/soot/jimple/infoflow/android/* src/main/java/soot/jimple/infoflow/android/`
4. Deleted `AXmlResourceParser`