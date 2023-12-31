from parsed_graph import Graph, Node
from definition import ResourceName, ComponentGroup, BoundaryGroup,DataStoreGroup
from typing import Tuple, Iterable, List

def filter_component(g: Graph):
    components = []
    for data in ComponentGroup:
        for component in data.value:
            components.append(component)

    result = g.FindResource(components)
    for i in result:
        print(i.label)

def filter_boundary(g: Graph):
    boundaries = []
    for data in BoundaryGroup:
        for boundary in data.value:
            boundaries.append(boundary)
    result = g.FindResource(boundaries)
    for i in result:
        print(i.label)

def filter_data_store(g: Graph):
    dataStores = []
    for data in DataStoreGroup:
        for dataStore in data.value:
            dataStores.append(dataStore)
    result = g.FindResource(dataStores)
    for i in result:
        print(i.label)

def filter_vpc(g: Graph) -> Iterable[Node]:
    return g.FindResource(AwsResource.VPC)


def identify_subnet(subnetLists: Iterable[Node]) -> Tuple[List[Node], List[Node]]:
    # Checking whether a direct connection from subnet to NAT
    public = []
    private = []

    for subnet in subnetLists:
        # Finding if any nat gateway point to subnet
        if len(list(filter(
            lambda x: x.CheckResourceType(AwsResource.NAT_GATEWAY), subnet.fromNodes))) > 0:
            public.append(subnet)
        else:
            private.append(subnet)

    return public, private


def find_subnets(vpc: Node) -> Tuple[List[Node], List[Node]]:
    subnets = filter(lambda x: x.CheckResourceType(AwsResource.SUBNET), vpc.fromNodes)
    return identify_subnet(subnets)

def find_resource_in_subnet(subnet: Node) -> Iterable[Node]:
    # DFS ->  Iterate to all resource in this subnet
    stack:List[Node] = [node for node in subnet.fromNodes]
    visited = set(stack)

    while len(stack) > 0:
        current = stack.pop()
        visited.add(current)
        for relatedNode in current.fromNodes:
            if relatedNode not in visited:
                stack.append(relatedNode)
    
    # filter resource only
    return filter(lambda x: x.IsResource(), visited)