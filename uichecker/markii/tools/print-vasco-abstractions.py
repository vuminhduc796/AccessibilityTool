import json
import sys
from typing import Any, List, Mapping, Tuple
from pydantic.tools import parse_obj_as
from common import MethodAbs, get_metrics

with open(sys.argv[1], "r") as f:
    dump: Mapping[str, List[Tuple[str, Any]]] = json.load(f)

for method, abs_json in dump.items():
    abstractions = parse_obj_as(MethodAbs, abs_json)
    metrics = get_metrics(abstractions)

    print("=====" * 20)
    print("===== Method: " + method)
    print(abstractions.body)
    for stmt, details in abstractions.abstractions:
        print(" > " + stmt)
        print("    - Local:")
        for k, v in details.localNodeMap.items():
            print(f"      - {k}: {v}")
        print("    - Global:")
        for k, v in details.globalNodeMap.items():
            print(f"      - {k}: {v}")
        print("    - Node handlers:")
        for nodeID, event, methods in details.nodeHandlerMap:
            print(f"      - {nodeID}, {event}: {methods}")
        print("    - Dialog handlers:")
        for nodeID, event, methods in details.dialogHandlerMap:
            print(f"      - {nodeID}, {event}: {methods}")
        print()
    print()
    print()