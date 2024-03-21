#!/usr/bin/python3
import json
import fire
import logging
import graphviz

from dfdgraph import DataStore
from dfdgraph.component import COMPONENT_ID_NODE
from dfdgraph.trustboundary import BOUNDARY_ID_NODE
from graph import LoadFromFolder
from dfdgraph import Diagram, Process, TrustBoundary
from tfparser.tfgrep import GetSemgrepJSON
from utils.n4j_helper import CleanUp, CompressNode, FindOwn, GetListParent, GetPathID, QueryAllConnectionResource, QueryGroup, QueryOutermostBoundary, QueryTagged, RemovePublicBoundaries, TaggingNode, TaggingPublic
from utils.yaml_importer import print_object, read_config

logging.basicConfig(level = logging.INFO)


def main(in_path, anno_path="./input/aws_annotation.yaml", rule_path="./input/aws_rule.yaml", sem_rule="./input/semgrep_rule.yaml", out_path="./output", reinit=True, graph_mode=False):
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
    
    publics = set(
        [m["tf_name"] for c in anno["processes"] for m in c["members"] if m.get("can_public", False)] + \
        [m["tf_name"] for c in anno["data_stores"] for m in c["members"] if m.get("can_public", False)]
    )

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
    for v in rule["publics"]:
        name = v["variable"]

        list_of_public_bound = set([result["extra"]["metavars"][name]["abstract_content"] for result in sem_json["results"]])
        logging.info(f"Public boundary {list_of_public_bound}")
        for bound in list_of_public_bound:
            TaggingPublic(pathID, bound)

    RemovePublicBoundaries(pathID)

    procname = set(c["group_name"] for c in anno["processes"])
    dsname = set(c["group_name"] for c in anno["data_stores"])
    boundname = set(c["group_name"] for c in anno["boundaries"])

    logging.info("List of Boundaries")
    
    bounds = set()
    compos = set()
    diag = Diagram()
    
    for r in QueryTagged(pathID, "boundaries"):
        id_ = str(r["id"])
        crafted_name = "%s (%s)" % (r["group"], r["general_name"])
        logging.info(f"{id_} - {crafted_name}")
        bounds.add(TrustBoundary(id_, crafted_name))

    logging.info("Traversing through owning rules")
    for v in rule["relations"]["own"]:
        r = FindOwn(v["first_node"], v["second_node"], v["method"], pathID)
        for u in r: 
            print(u)
            crafted_name1 = "%s (%s)" % (u["group1"], u["general_name1"])
            crafted_name2 = "%s (%s)" % (u["group2"], u["general_name2"])
            if u["group1"] in boundname:
                fr = BOUNDARY_ID_NODE.get(str(u["id1"]), TrustBoundary(u["id1"], crafted_name1))
            elif u["group1"] in procname:
                fr = COMPONENT_ID_NODE.get(str(u["id1"]), Process(u["id1"], crafted_name1))
            elif u["group1"] in dsname:
                fr = COMPONENT_ID_NODE.get(str(u["id1"]), DataStore(u["id1"], crafted_name1))

                
            if u["group2"] in boundname:
                if u["id1"] in BOUNDARY_ID_NODE and u["id2"] in BOUNDARY_ID_NODE:
                    continue
                to = BOUNDARY_ID_NODE.get(str(u["id2"]), TrustBoundary(u["id2"], crafted_name2))
                if u["group1"] not in boundname:
                    to.AddNode(fr)
                    bounds.add(to)
                    compos.add(fr)
                    if u["name1"] in publics:
                        diag.AddPublicNode(fr)
                else:
                    fr.AddInnerBound(to)
                    bounds.add(to)
                    bounds.add(fr)
            elif u["group2"] in procname:
                if u["id1"] in BOUNDARY_ID_NODE and u["id2"] in COMPONENT_ID_NODE:
                    continue
                to = COMPONENT_ID_NODE.get(str(u["id2"]), Process(u["id2"], crafted_name2))
                fr.AddNode(to)
                bounds.add(fr)
                compos.add(to)
                # if u["name2"] in publics:
                #     diag.AddPublicNode(to)
            elif u["group2"] in dsname:
                if u["id1"] in BOUNDARY_ID_NODE and u["id2"] in COMPONENT_ID_NODE:
                    continue
                to = COMPONENT_ID_NODE.get(str(u["id2"]), DataStore(u["id2"], crafted_name2))
                fr.AddNode(to)
                bounds.add(fr)
                compos.add(to)
                # if u["name2"] in publics:
                #     diag.AddPublicNode(to)
            logging.info(type(fr).__name__ + str(fr.name))
            logging.info(type(to).__name__ + str(to.name))

    # Add boundaries to graph
    aws = TrustBoundary("", "AWS")
    diag.AddBoundary(aws)

    for r in QueryTagged(pathID, "processes") + QueryTagged(pathID, "data_stores"):
        id_ = str(r["id"])
        if id_ in compos:
            continue
        crafted_name = "%s (%s)" % (r["group"], r["general_name"])
        logging.info(f"{id_} - {crafted_name}")
        if r["group"] in procname:
            n = COMPONENT_ID_NODE.get(id_, Process(id_, crafted_name))
        else:
            n = COMPONENT_ID_NODE.get(id_, DataStore(id_, crafted_name))
        aws.AddNode(n)
        logging.info(crafted_name)    
        if r["name"] in publics:
            diag.AddPublicNode(n)



    for r in QueryOutermostBoundary(pathID):
        id_ = str(r["id"])
        crafted_name = "%s (%s)" % (r["group"], r["general_name"])
        aws.AddInnerBound(BOUNDARY_ID_NODE.get(id_))
        logging.info("OUTER " + crafted_name)

    for r in QueryAllConnectionResource(pathID):
        crafted_name1 = "%s (%s)" % (r["group1"], r["general_name1"])
        crafted_name2 = "%s (%s)" % (r["group2"], r["general_name2"])
        # print(r)
        logging.info(crafted_name1 + "-->" + crafted_name2)
        COMPONENT_ID_NODE.get(str(r["id1"])).AddEdge(COMPONENT_ID_NODE.get(str(r["id2"])))
        COMPONENT_ID_NODE.get(str(r["id2"])).AddEdge(COMPONENT_ID_NODE.get(str(r["id1"])))
            
        
    # Fill with connections
    
    if graph_mode:
        g = graphviz.Digraph("G", directory="output", filename="result.dot")
        diag.DrawDiagram(g)
        g.render(filename="out", format="png", view=False)
    else:
        diag.ExportSparta()

    

if __name__ == '__main__':
    fire.Fire(main)
