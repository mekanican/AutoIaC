from graph import Node
from typing import Iterable

def debug_node_list(nodes: Iterable[Node]):
    for n in nodes:
        print("\t- " + n.label)