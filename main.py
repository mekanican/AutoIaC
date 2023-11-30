#!/usr/bin/python3
import fire
import json
from pytm.pytm import TM, Server, Boundary
from parsed_graph import *
from typing import Set, Tuple, Iterable
import logging
logging.basicConfig(level = logging.INFO)

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


def main(in_path, out_path="./output"):
    print(f"Reading {in_path}, Writing to {out_path}")
    g = Graph.LoadFromFolder(in_path)
    vpcs = filter_vpc(g)

    tm = TM("AWS Threat Model")
    tm.isOrdered = True

    for vpc in vpcs:
        print("Working on VPC:", vpc.label)
        
        # VPC Consist of public & private
        # Private & public consist of resources in subnets
        vpcBound = Boundary(vpc.label)

        # Public bound = vpc
        privateBound = Boundary("Private")
        privateBound.inBoundary = vpcBound

        pub, priv = find_subnets(vpc)
        print("List of public subnet:")
        for sub in pub:
            print(sub.label)
            refResources = find_resource_in_subnet(sub)
            for ref in refResources:
                print("-", ref.label)
                # Temporary, TODO: classify resource -> correct TM element
                server = Server(ref.label)
                server.inBoundary = vpcBound
            
        print("List of private subnet:")
        for sub in priv:
            print(sub.label)
            refResources = find_resource_in_subnet(sub)
            for ref in refResources:
                print("-", ref.label)
                server = Server(ref.label)
                server.inBoundary = privateBound
        print("------------------------")
    print("Extracting Dotfile to output")
    
    with open(out_path + "/output.dot", "w") as f:
        f.write(tm.dfd())
    

if __name__ == '__main__':
    fire.Fire(main)
