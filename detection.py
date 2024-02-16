from parsed_graph import Graph, Node
from annotation import GroupName, ComponentGroup, BoundaryGroup, DataStoreGroup
from typing import Iterable

def filter_template(g: Graph, type):
    components = []
    for data in type:
        for component in data.value:
            components.append(component)

    return g.FindResource(components)

def filter_component(g: Graph):
    return filter_template(g, ComponentGroup)

def filter_boundary(g: Graph):
    return filter_template(g, BoundaryGroup)

def filter_data_store(g: Graph):
    return filter_template(g, DataStoreGroup)

# Function to specialize group to parse (usually Boundaries)
def filter_group(i: Iterable[Node], name: GroupName) -> Iterable[Node]:
    return filter(lambda x: x.rescType in name, i)
