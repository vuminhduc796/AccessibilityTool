## Overview of MarkII analysis

- Event-driven inter-procedural control flow analysis
- GUI-fact data-flow analysis & summarization
- Other pre-analysis: pointer analysis, intent analysis (depending on another standalone tool called IC3) etc.
- Customizable state transition analysis (https://github.com/izgzhen/markii/wiki/Configure-State-Transition-Analysis)

For example, MarkII knows (1) Given an activity, what events might be handled within it and by what handlers;
(2) What views are constructed and added to the activity's GUI dynamically when it is created?
(3) Which privileged APIs are invoked (and what permissions are used) -- currently, only a few are supported (e.g.
[readAudio](https://blog.zhen-zhang.com/markii/api/com/research/nomad/markii/FactsWriter$$Fact$.html#readAudio:com.research.nomad.markii.FactsWriter.Fact.Value))

## Roadmap

Current focus:

- Consolidate and refactor to support a second client besides [ui-checker](https://github.com/izgzhen/ui-checker).
The general feature is a scalable extraction of a finite-state machine. Need more time to break it down into concrete features.

## Important resources

- [Codebase](https://github.com/izgzhen/markii/wiki/Codebase)
- [Developer Guide](https://github.com/izgzhen/markii/wiki/Developer-Guide)
- [Soot Doc (develop)](https://soot-build.cs.uni-paderborn.de/public/origin/develop/soot/soot-develop/jdoc/)
    * This is not easy to use. Recommend to just look up doc inside an IDE, or fix https://github.com/izgzhen/markii/issues/47.