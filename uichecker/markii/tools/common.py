from typing import List, Mapping, Tuple
from pydantic import BaseModel

class MethodAbsDetails(BaseModel):
    localNodeMap: Mapping[str, List[Tuple[str, str]]]
    globalNodeMap: Mapping[str, List[Tuple[str, str]]]
    nodeHandlerMap: List[Tuple[str, str, List[str]]]
    dialogHandlerMap: List[Tuple[str, str, List[str]]]

class MethodAbs(BaseModel):
    abstractions: List[Tuple[str, MethodAbsDetails]]
    body: str

def get_metrics(method_abs: MethodAbs):
    return [{
        "unit": unit,
        "metrics": {
            "local_node_map_size": len(abstraction.localNodeMap),
            "global_node_map_size": len(abstraction.globalNodeMap),
        },
        "values": {
            "local_node_map": abstraction.localNodeMap,
            "global_node_map": abstraction.globalNodeMap,
        }
    } for unit, abstraction in method_abs.abstractions ]