from typing import Iterable, Tuple, List
from graph import Node
from annotation import AwsResource
from utils import is_connected

def aws_identify_subnet(subnetLists: Iterable[Node]) -> Tuple[List[Node], List[Node]]:
    # Checking whether a direct connection from subnet to NAT
    public = []
    private = []

    for subnet in subnetLists:
        # Finding if any nat gateway point to subnet
        if any(filter(lambda x: x.CheckResourceType(AwsResource.NAT_GATEWAY), subnet.fromNodes)):
            public.append(subnet)
        else:
            private.append(subnet)

    return public, private

# Find Subnet belong to specified VPC
def aws_subnet_relation(subnets: Iterable[Node], vpc: Node):
    # Subnet ->  VPC
    return filter(lambda x: is_connected(x, vpc), subnets)

# Find Component belong to specified Security group
def aws_security_group_relation(components: Iterable[Node], secGroup: Node):
    # Component ->  Security Group
    return filter(lambda x: is_connected(x, secGroup), components)

# Find Components related to subnet
def aws_component_relation(components: Iterable[Node], subnet: Node):
    # Component ->  Subnet
    return filter(lambda x: is_connected(x, subnet), components)

# TODO: Data store

def aws_component2component(components: Iterable[Node], target: Node, isTarget=True):
    copyComponents = filter(lambda x: x is not target, components)
    if isTarget:
        return filter(lambda x: is_connected(x, target), copyComponents)
    else:
        return filter(lambda x: is_connected(target, x), copyComponents)