#!/usr/bin/python3
import fire
# import json
# from pytm.pytm import TM, Server, Boundary
from parsed_graph import *
from detection import *
import logging
logging.basicConfig(level = logging.INFO)


def main(in_path, out_path="./output"):
    print(f"Reading {in_path}, Writing to {out_path}")
    g = Graph.LoadFromFolder(in_path, False)
    for c in filter_component(g): print(c.label)
    print("----")
    for b in filter_boundary(g): print(b.label)
    print("----")
    for ds in filter_data_store(g): print(ds.label)
    print("----")
    for z in filter_group(filter_boundary(g), BoundaryGroup.VIRTUAL_NETWORK): print(z.label)
    print("----")
    return
    vpcs = filter_vpc(g)

    # tm = TM("AWS Threat Model")
    # tm.isOrdered = True

    for vpc in vpcs:
        print("Working on VPC:", vpc.label)
        
        # VPC Consist of public & private
        # Private & public consist of resources in subnets
        # vpcBound = Boundary(vpc.label)

        # Public bound = vpc
        # privateBound = Boundary("Private")
        # privateBound.inBoundary = vpcBound

        pub, priv = find_subnets(vpc)
        print("List of public subnet:")
        for sub in pub:
            print(sub.label)
            refResources = find_resource_in_subnet(sub)
            for ref in refResources:
                print("-", ref.label)
                # Temporary, TODO: classify resource -> correct TM element
                # server = Server(ref.label)
                # server.inBoundary = vpcBound
            
        print("List of private subnet:")
        for sub in priv:
            print(sub.label)
            refResources = find_resource_in_subnet(sub)
            for ref in refResources:
                print("-", ref.label)
                # server = Server(ref.label)
                # server.inBoundary = privateBound
        print("------------------------")
    print("Extracting Dotfile to output")
    
    # with open(out_path + "/output.dot", "w") as f:
        # f.write(tm.dfd())

    print(filter_component(g))
    

if __name__ == '__main__':
    fire.Fire(main)
