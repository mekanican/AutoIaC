#!/usr/bin/python3
import fire
import json

jsonData = {}
nodeMap = {}

"""
Sample Node format
---------------------------------------------------------
{
    "data": {
        "id": "module.root.module.network.aws_vpc.km_vpc",
        "parent": "module.root.module.network",
        "label": "aws_vpc.km_vpc",
        "type": "resource"
    },
    "classes": [
        "resource"
    ]
}
"""
def filter_vpc():
    return filter(lambda elem: elem["data"]["label"].startswith("aws_vpc."), jsonData["nodes"])

# Return mapping id -> node
def create_node_map():
    result = {}
    for elem in jsonData["nodes"]:
        result[elem["data"]["id"]] = elem
    return result


def identify_subnet(subnetLists):
    # Checking whether a direct connection from subnet to NAT
    public = []
    private = []
    # 0 -> private, 1 -> public
    flags = [0] * len(subnetLists)
    idx = 0
    for subnet in subnetLists:
        subnetId = subnet["data"]["id"]
        for edge in jsonData["edges"]: # TODO: improve performance
            if edge["data"]["target"] == subnetId:
                source = nodeMap[edge["data"]["source"]]
                if source["data"]["label"].startswith("aws_nat_gateway."):
                    flags[idx] = 1
            
        idx += 1

    for i in range(len(flags)):
        if flags[i] == 1:
            public.append(subnetLists[i])
        else:
            private.append(subnetLists[i])
    
    return public, private

"""
Sample Edge format
---------------------------------------------------------
{
    "data": {
        "id": "module.root.module.network.aws_subnet.km_private_subnet-module.root.module.network.aws_vpc.km_vpc",
        "source": "module.root.module.network.aws_subnet.km_private_subnet",
        "target": "module.root.module.network.aws_vpc.km_vpc",
        "sourceType": "resource",
        "targetType": "resource"
    },
    "classes": [
        "resource-resource"
    ]
}
"""

def find_subnets(vpc):
    subnets = []
    # Find all aws_subnet that use info of this vpc
    vpcId = vpc["data"]["id"]
    for elem in jsonData["edges"]:
        if elem["data"]["target"] == vpcId:
            source = nodeMap[elem["data"]["source"]]
            if source["data"]["label"].startswith("aws_subnet."):
                subnets.append(source)
    return identify_subnet(subnets)

def find_resource_in_subnet(subnet):
    subnetId = subnet["data"]["id"]

    resources = []
    
    # Case 1: Resource connect directly to subnet
    for elem in jsonData["edges"]:
        if elem["data"]["target"] == subnetId and elem["data"]["sourceType"] == "resource":
            source = nodeMap[elem["data"]["source"]]
            # Ignore the aws_nat_gateway & aws_route_table_association
            if source["data"]["label"].startswith("aws_nat_gateway.") or \
                source["data"]["label"].startswith("aws_route_table_association"):
                    continue
            resources.append(source)
            
    # Case 2: subnet -> output -> variable -> resource
    # Find outputs
    outputs = []
    for elem in jsonData["edges"]:
        if elem["data"]["target"] == subnetId and elem["data"]["sourceType"] == "output":
            source = nodeMap[elem["data"]["source"]]
            outputs.append(source)
    # Find referenced variables
    vars = []
    for output in outputs:
        outputId = output["data"]["id"]
        for elem in jsonData["edges"]:
            source = nodeMap[elem["data"]["source"]]
            if elem["data"]["target"] == outputId and elem["data"]["sourceType"] == "var":
                vars.append(source)
    # Find referenced resources
    for var in vars:
        varId = var["data"]["id"]
        for elem in jsonData["edges"]:
            source = nodeMap[elem["data"]["source"]]
            if elem["data"]["target"] == varId and elem["data"]["sourceType"] == "resource":
                resources.append(source)

    # TODO: handle special case (graph traversal to accessing all resources)
    return resources


def main(in_path, out_path="./output"):
    global jsonData
    global nodeMap
    
    print(f"Reading {in_path}, Writing to {out_path}")
    jsonData = json.load(open(in_path, "r"))
    nodeMap = create_node_map()
    vpcs = filter_vpc()
    for vpc in vpcs:
        print("Working on VPC:", vpc["data"]["id"])
        pub, priv = find_subnets(vpc)
        print("List of public subnet:")
        for sub in pub:
            print(sub["data"]["id"])
            refResources = find_resource_in_subnet(sub)
            for ref in refResources:
                print("-", ref["data"]["id"])
            
        print("List of private subnet:")
        for sub in priv:
            print(sub["data"]["id"])
            refResources = find_resource_in_subnet(sub)
            for ref in refResources:
                print("-", ref["data"]["id"])
            
        print("------------------------")

if __name__ == '__main__':
    fire.Fire(main)
