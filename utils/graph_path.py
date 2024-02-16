from typing import Set, Any
# from graph import Node
from functools import lru_cache
# Check directional path from A ->  B
@lru_cache
def is_connected(a: Any, b: Any):
    if a is b:
        return True

    def dfs(m: Any, n: Any, visited: Set):
        if m is n:
            return True
        visited.add(m)
        # print(m.label, "-->", n.label)
        for nxt in m.toNodes:
            if nxt not in visited and dfs(nxt, n, visited):
                return True
        return False

    return dfs(a, b, set())