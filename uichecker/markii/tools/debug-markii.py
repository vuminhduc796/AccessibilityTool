from msbase.utils import load_json
import glob
import sys
from collections import OrderedDict
from termcolor import colored

method_states = {} # type: ignore

markii_debug_dir = "markii-debug"
localMap = 'localNodeMap'
globalMap = None
aliases = None
verbose = False

if len(sys.argv) > 1:
    if "custom" in sys.argv:
        markii_debug_dir = "markii-custom-debug"
        localMap = 'localMap'
        globalMap = 'globalMap'
        aliases = "aliases"
    if "-v" in sys.argv:
        verbose = True

for json_file in glob.glob("/tmp/" + markii_debug_dir + "/*.json"):
    split = json_file.split("@")
    method = split[0]
    idx = int(split[1].strip(".json"))
    if method not in method_states:
        method_states[method] = {}
    method_states[method][idx] = {
        "content": load_json(json_file),
        "file": json_file
    }

for method, indexed_states in method_states.items():
    print("====== Method " + method + " ======")
    prev_printed = True
    for idx, state_dict in OrderedDict(sorted(indexed_states.items())).items():
        state = state_dict["content"]
        f = state_dict["file"]
        printed = verbose
        colored_vars = set()
        state_lines =[]
        for v, ps in state["domain"][localMap].items():
            colored_vars.add(v)
            for path_data in ps[:10]:
                printed = True
                assert len(path_data) == 2
                path, data = path_data
                if path != "":
                    path = path + " ==> "
                state_lines.append("- %s: %s%s" % (colored(v, "green"), path, data))
            if len(ps) > 10:
                state_lines.append("- ...")
        if globalMap:
            for v, ps in state["domain"][globalMap].items():
                colored_vars.add(v)
                for path_data in ps[:10]:
                    printed = True
                    assert len(path_data) == 2
                    path, data = path_data
                    if path != "":
                        path = path + " ==> "
                    state_lines.append("- %s: %s%s" % (colored(v, "green"), path, data))
                if len(ps) > 10:
                    state_lines.append("- ...")
        if aliases:
            for v, refs in state["domain"][aliases].items():
                colored_vars.add(v)
                state_lines.append("- %s ~~> %s" % (colored(v, "green"), refs))
        if printed and not prev_printed:
            unit = indexed_states[idx - 1]["content"]["unit"]
            for v in colored_vars:
                unit = unit.replace(v, colored(v, "green"))
            print("=== %s: %s" % (colored(str(idx - 1), "yellow"), unit))
            print()
        if printed:
            print("FILE: " + f)
            print(state["domainSize"])
            print("\n".join(state_lines))
        if printed:
            unit = state["unit"]
            for v in colored_vars:
                unit = unit.replace(v, colored(v, "green"))
            print("\n=== %s: %s" % (colored(str(idx), "yellow"), unit))
            print()
        prev_printed = printed