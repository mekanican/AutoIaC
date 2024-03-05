#!/usr/bin/python3
import fire
import logging
import graphviz

from dfdgraph import DataStore
from dfdgraph import GLOBAL_DF
from graph import Graph
from rule.filter import filter_group, filter_component, filter_boundary, filter_data_store
from dfdgraph import Diagram, Process, TrustBoundary
from rule.aws_relation import aws_subnet_relation, aws_identify_subnet, aws_component_relation, aws_component2component
from annotation import BoundaryGroup
from threatparser import FlowThreat
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

    # TODO: optimize
    node_2_dfdnode = {}


    # Show datastore first
    for ds in dataStores:
        data = DataStore(ds.label)
        aws.AddNode(data)

        # TODO: check is public datastore
        # diag.AddPublicNode(data)
        node_2_dfdnode[ds] = data

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
                node_2_dfdnode[component] = p

        # Assumption: no public subnet => every component is public
        # Correct way: check route table with CDIR 0.0.0.0/0 & Target internet gateway
        # Or: map_public_ip_on_launch in subnet
        # TODO: implement improve hcl parser to link info to resource.
        if len(public) == 0:
            for sub in private:
                logging.info("-> Process " + sub.label)
                # Find components related to this subnet
                for component in aws_component_relation(components, sub):
                    p = Process(component.label)
                    v.AddNode(p)
                    processedNodes.add(component)
                    diag.AddPublicNode(p)
                    # print("-<<", component.label)
                    node_2_dfdnode[component] = p
            continue
            
                
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
                node_2_dfdnode[component] = p
    
    # Keep the rest in AWS's boundary and assume the publicity    
    for other in set(components).difference(processedNodes):
        p = Process(other.label)
        aws.AddNode(p)
        diag.AddPublicNode(p)
        node_2_dfdnode[other] = p
        # print("-<<<", component.label)

    # TODO: Component 2 component connection
    components_ds = set(components).union(set(dataStores))
    for u in components_ds:
        for c in aws_component2component(components_ds, u, False):
            node_2_dfdnode[u].AddEdge(node_2_dfdnode[c])
            # print(u.module, u.parent, u.label, c.module, c.parent, c.label)
        # Redundant!
        # for c in aws_component2component(components_ds, u, True):
        #     node_2_dfdnode[c].AddEdge(node_2_dfdnode[u])
        #     print(c.module, c.parent, c.label, u.module, u.parent, u.label)
            
    # for u,v in combinations(components_ds, 2):
    #     aws_component2component()
    #     pass

        
    # TODO: (BUG) Cannot generate diagram & make sparta due to duplicate DataFlow
    diag.DrawDiagram(g)
    g.render(filename="out", format="png", view=False)
    
    # print("Threat analyzing -----------")

    # # Showing threat:
    # threats = FlowThreat.read()
    # for df in GLOBAL_DF:
    #     print(df.fromNode.name, "->", df.toNode.name)
    #     for threat in threats:
    #         if threat.check(df):
    #             print("- Name", threat.threatName)
    #             print("- Description", threat.description)
    #             print("------")
    #     print("")

    #print("SPARTA Exporting --------------")
    #diag.ExportSparta()
    
    

if __name__ == '__main__':
    fire.Fire(main)
