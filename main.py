#!/usr/bin/python3
import fire
import logging
import graphviz

from dfdgraph.component import DataStore
from graph import Graph
from rule.filter import filter_group, filter_component, filter_boundary, filter_data_store
from dfdgraph import Diagram, Process, TrustBoundary
from rule.aws_relation import aws_subnet_relation, aws_identify_subnet, aws_component_relation, aws_component2component
from annotation import BoundaryGroup
from utils import debug_node_list

logging.basicConfig(level = logging.INFO)


def main(in_path, out_path="./output", reinit=True):
    print(f"Reading {in_path}, Writing to {out_path}")
    g = Graph.LoadFromFolder(in_path, reinit)

    components = list(filter_component(g))
    boundaries = list(filter_boundary(g))
    dataStores = list(filter_data_store(g))

    vpcs = list(filter_group(boundaries, BoundaryGroup.VIRTUAL_NETWORK))
    secGroups = list(filter_group(boundaries, BoundaryGroup.VIRTUAL_FIREWALL))
    subnets = list(filter_group(boundaries, BoundaryGroup.SUBNET))

    print("Found components")
    debug_node_list(components)
    print("Found boundaries")
    debug_node_list(boundaries)
    print("Found data stores")
    debug_node_list(dataStores)
    
    print("---")

    print("Found VPC")
    debug_node_list(vpcs)
    print("Found Subnet")
    debug_node_list(subnets)
    print("Found Security Group")
    debug_node_list(secGroups)


    processedNodes = set()

    g = graphviz.Digraph("G", directory="output", filename="result.dot")
    diag = Diagram()

    # AWS global trust boundary
    aws = TrustBoundary("AWS")
    diag.AddBoundary(aws)


    # Show datastore first
    for ds in dataStores:
        data = DataStore(ds.label)
        aws.AddNode(data)
        diag.AddPublicNode(data)

    # Each VPC has Boundaries
    for vpc in vpcs:
        logging.info("Process " + vpc.label)
        v = TrustBoundary(vpc.label)
        aws.AddInnerBound(v)

        relatedSubnets = list(aws_subnet_relation(subnets, vpc))
        public, private = aws_identify_subnet(relatedSubnets)

        # Public subnet go to VPC trust boundaries
        for sub in public:
            logging.info("-> Process " + sub.label)
            # Find components related to this subnet
            for component in aws_component_relation(components, sub):
                p = Process(component.label)
                v.AddNode(p)
                processedNodes.add(component)
                # diag.AddPublicNode(p)
                # print("-<", component.label)
        if len(private) == 0:
            continue
        priv = TrustBoundary("Private Subnet")
        v.AddInnerBound(priv)
        # Private subnet go to Private trust boundaries
        for sub in private:
            logging.info("-> Process " + sub.label)
            # Find components related to this subnet
            for component in aws_component_relation(components, sub):
                p = Process(component.label)
                priv.AddNode(p)
                processedNodes.add(component)
                # print("-<<", component.label)
        
    for other in set(components).difference(processedNodes):
        p = Process(other.label)
        aws.AddNode(p)
        diag.AddPublicNode(p)
        # print("-<<<", component.label)

    # TODO: Component 2 component connection
    # TODO: Fix why aws_instance in private subnet
        
    diag.DrawDiagram(g)
    g.render(filename="out", format="png", view=False)
    

if __name__ == '__main__':
    fire.Fire(main)
