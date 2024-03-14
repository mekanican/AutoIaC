#!/usr/bin/python3
import json
import fire
import logging
import graphviz

from dfdgraph import DataStore
from graph import LoadFromFolder
from dfdgraph import Diagram, Process, TrustBoundary
from tfparser.tfgrep import GetSemgrepJSON
from utils.n4j_helper import CleanUp, CompressNode, GetListParent, GetPathID, QueryGroup, QueryTagged, TaggingNode, TaggingPublic
from utils.yaml_importer import print_object, read_config

logging.basicConfig(level = logging.INFO)


def main(in_path, anno_path="./input/aws_annotation.yaml", rule_path="./input/aws_rule.yaml", sem_rule="./input/semgrep_rule.yaml", out_path="./output", reinit=True):
    print(f"Reading {in_path}, Writing to {out_path}")

    anno = read_config(anno_path)
    rule = read_config(rule_path)

    print("ANNOTATION")
    print_object(anno)
    print("RULE")
    print_object(rule)

    # Process compressed first

    compresses = \
        [m["tf_name"] for c in anno["processes"] for m in c["members"] if m.get("compress", False)] + \
        [m["tf_name"] for c in anno["data_stores"] for m in c["members"] if m.get("compress", False)]
    

    # Cleaning up (FOR DEBUGGING ONLY)
    CleanUp()

    # Getting path id
    pathID = LoadFromFolder(in_path, init=reinit)
    print("-----")

    parents = GetListParent(pathID)
    print(parents)
    print(compresses)
    for parent in parents:
        for compress in compresses:
            logging.info(f"Process {compress} in {parent}")
            CompressNode(compress, parent, pathID)
            
    for key in anno:
        for c in anno[key]:
            for member in c["members"]:
                TaggingNode(member["tf_name"], pathID, c["group_name"], member["name"], key)

    sem_json = json.load(open(GetSemgrepJSON(in_path, sem_rule), "r"))
    list_of_public_subnet = set([result["extra"]["metavars"]["$SN_NAME"]["abstract_content"] for result in sem_json["results"]])
    logging.info(f"Public subnet {list_of_public_subnet}")
    for subnet in list_of_public_subnet:
        TaggingPublic(pathID, subnet)

        
    # for relation in rule["relations"]["own"]:
    #     first = relation["first_node"]
    #     second = relation["second_node"]
    #     method = relation["method"]

    #     result = QueryGroup(pathID, first, second)
    #     for r in result:

    #         pass
    #     pass
    
    diag = Diagram()
    aws = TrustBoundary("AWS")
    diag.AddBoundary(aws)
    diag.ExportSparta()
            
    exit(0)

    # PHASE 1: EXTRACT BARE COMPONENT (PROCESS + DATA STORE)
    

    
    # g = LoadFromFolder(in_path, reinit)

    # components = list(filter_component(g))
    # boundaries = list(filter_boundary(g))
    # dataStores = list(filter_data_store(g))

    # vpcs = list(filter_group(boundaries, BoundaryGroup.VIRTUAL_NETWORK))
    # secGroups = list(filter_group(boundaries, BoundaryGroup.VIRTUAL_FIREWALL))
    # subnets = list(filter_group(boundaries, BoundaryGroup.SUBNET))


    # processedNodes = set()

    g = graphviz.Digraph("G", directory="output", filename="result.dot")
    diag = Diagram()

    # AWS global trust boundary
    aws = TrustBoundary("AWS")
    diag.AddBoundary(aws)

    # # TODO: optimize
    # node_2_dfdnode = {}


    # # Show datastore first
    # for ds in dataStores:
    #     data = DataStore(ds.label)
    #     aws.AddNode(data)

    #     # TODO: check is public datastore
    #     # diag.AddPublicNode(data)
    #     node_2_dfdnode[ds] = data

    # # Each VPC has Boundaries
    # for vpc in vpcs:
    #     logging.info("Process " + vpc.label)
    #     v = TrustBoundary(vpc.label)
    #     aws.AddInnerBound(v)

    #     relatedSubnets = list(aws_subnet_relation(subnets, vpc))
    #     public, private = aws_identify_subnet(relatedSubnets)

    #     # Public subnet go to VPC trust boundaries
    #     for sub in public:
    #         logging.info("-> Process " + sub.label)
    #         # Find components related to this subnet
    #         for component in aws_component_relation(components, sub):
    #             p = Process(component.label)
    #             v.AddNode(p)
    #             processedNodes.add(component)
    #             # diag.AddPublicNode(p)
    #             # print("-<", component.label)
    #             node_2_dfdnode[component] = p

    #     # Assumption: no public subnet => every component is public
    #     # Correct way: check route table with CDIR 0.0.0.0/0 & Target internet gateway
    #     # Or: map_public_ip_on_launch in subnet
    #     # TODO: implement improve hcl parser to link info to resource.
    #     if len(public) == 0:
    #         for sub in private:
    #             logging.info("-> Process " + sub.label)
    #             # Find components related to this subnet
    #             for component in aws_component_relation(components, sub):
    #                 p = Process(component.label)
    #                 v.AddNode(p)
    #                 processedNodes.add(component)
    #                 diag.AddPublicNode(p)
    #                 # print("-<<", component.label)
    #                 node_2_dfdnode[component] = p
    #         continue
            
                
    #     if len(private) == 0:
    #         continue
    #     priv = TrustBoundary("Private Subnet")
    #     v.AddInnerBound(priv)
    #     # Private subnet go to Private trust boundaries
    #     for sub in private:
    #         logging.info("-> Process " + sub.label)
    #         # Find components related to this subnet
    #         for component in aws_component_relation(components, sub):
    #             p = Process(component.label)
    #             priv.AddNode(p)
    #             processedNodes.add(component)
    #             # print("-<<", component.label)
    #             node_2_dfdnode[component] = p
    
    # # Keep the rest in AWS's boundary and assume the publicity    
    # for other in set(components).difference(processedNodes):
    #     p = Process(other.label)
    #     aws.AddNode(p)
    #     diag.AddPublicNode(p)
    #     node_2_dfdnode[other] = p
    #     # print("-<<<", component.label)

    # # TODO: Component 2 component connection
    # components_ds = set(components).union(set(dataStores))
    # for u in components_ds:
    #     for c in aws_component2component(components_ds, u, False):
    #         node_2_dfdnode[u].AddEdge(node_2_dfdnode[c])
    #         # print(u.module, u.parent, u.label, c.module, c.parent, c.label)
            

        
    # TODO: (BUG) Cannot generate diagram & make sparta due to duplicate DataFlow
    diag.DrawDiagram(g)
    g.render(filename="out", format="png", view=False)

    #print("SPARTA Exporting --------------")
    #diag.ExportSparta()
    
    

if __name__ == '__main__':
    fire.Fire(main)
