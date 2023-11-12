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
    # and aws_nat_gateway
    vpcId = vpc["data"]["id"]
    for elem in jsonData["edges"]:
        if elem["data"]["target"] == vpcId:
            source = nodeMap[elem["data"]["source"]]
            if source["data"]["label"].startswith("aws_subnet."):
                subnets.append(source)
    return identify_subnet(subnets)



def main(in_path, out_path="./output"):
    global jsonData
    global nodeMap
    
    print(f"Reading {in_path}, Writing to {out_path}")
    jsonData = json.load(open(in_path, "r"))
    nodeMap = create_node_map()
    vpcs = filter_vpc()
    for vpc in vpcs:
        print("Working on VPC:", vpc["data"]["label"])
        pub, priv = find_subnets(vpc)
        print("List of public subnet:")
        for sub in pub:
            print(sub["data"]["label"])
            
        print("List of private subnet:")
        for sub in priv:
            print(sub["data"]["label"])
            
        print("------------------------")

if __name__ == '__main__':
    fire.Fire(main)
