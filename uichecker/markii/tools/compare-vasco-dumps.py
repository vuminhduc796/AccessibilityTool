import json
import sys
from typing import Any, List, Mapping, Tuple
from pydantic.tools import parse_obj_as
from common import MethodAbs, get_metrics

with open(sys.argv[1], "r") as f:
    dump1: Mapping[str, List[Tuple[str, Any]]] = json.load(f)

with open(sys.argv[2], "r") as f:
    dump2: Mapping[str, List[Tuple[str, Any]]] = json.load(f)


for m in set(dump1.keys()).intersection(set(dump2.keys())):
    m_printed = False
    abs1 = dump1[m]
    abs2 = dump2[m]
    parsed1 = parse_obj_as(MethodAbs, abs1)
    parsed2 = parse_obj_as(MethodAbs, abs2)
    metrics1 = get_metrics(parsed1)
    metrics2 = get_metrics(parsed2)
    # assert len(metrics1) == len(metrics2)
    if len(metrics1) != len(metrics2):
        continue
    if metrics1 != metrics2:
        for s1, s2 in zip(metrics1, metrics2):
            unit = s1["unit"]
            # assert s1["unit"] == s2["unit"]
            if s1["unit"] != s2["unit"]:
                continue
            for k in s1["metrics"].keys():
                m1 = s1["metrics"][k]
                m2 = s2["metrics"][k]
                if m1 != m2:
                    print("- %s: %s != %s" % (k, m1, m2))
                    if m1 > m2:
                        if not m_printed:
                            print(f"===== Method {m} =====")
                            print(parsed1.body)
                            print()
                            m_printed = True
                        print(f"\t* [hint] method = {m}")
                        print(f"\t* [hint] unit = {unit}")
                        print("\t* [values] v1 = %s" % s1["values"][k[:-len("-size")]])
                        print("\t* [values] v2 = %s" % s2["values"][k[:-len("-size")]])
        print()