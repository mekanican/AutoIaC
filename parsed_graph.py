import json
from terraform_to_json import GetJSON
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
from typing import List, Type
from annotation import ResourceName, AwsResource


class Node:
    def __init__(self, provider: Type, kvargs: dict[str, str]):
        self.module = Node.ParseModule(kvargs["id"])
        self.parent = kvargs.get("parent", "")
        self.label = kvargs["label"]
        self.type = Type(kvargs["type"])
        self.fromNodes:List[Node] = []
        self.toNodes:List[Node] = []
        # Resource labeling
        resourceType = self.label.split(".")[0]
        try:
            self.rescType = provider(resourceType)
        except:
            self.rescType = None
    
    # module.root.module.network.aws_vpc.km_vpc
    # ID has multiple module layer ->  get last layer
    # And prioritize Resource type
    def ParseModule(id: str) -> str:
        splitted = id.split(".")
        idx = -1
        for i in range(len(splitted)):
            if splitted[i] == 'module':
                idx = i
        if idx == -1:
            return "" # Error
        module = splitted[idx+1]
        return module

    def AddFromNode(self, n: "Node"):
        self.fromNodes.append(n)
    def AddToNode(self, n: "Node"):
        self.toNodes.append(n)
    
    def IsVariable(self):
        return self.type == Type.VARIABLE
    def IsResource(self):
        return self.type == Type.RESOURCE
    def IsOutput(self):
        return self.type == Type.OUTPUT

    def CheckResourceType(self, t: ResourceName):
        return self.rescType == t
        
    
# Graph will initialize all the nodes and hold useful information about 3 types
class Graph:
    def __init__(self):
        self._vars: List[Node] = []
        self._outs: List[Node] = []
        self._rescs: List[Node] = []

    def AddVariable(self, n: Node):
        self._vars.append(n)
    def AddOutput(self, n: Node):
        self._outs.append(n)
    def AddResource(self, n: Node):
        self._rescs.append(n)

    def FindResource(self, t: List[ResourceName]):
        return filter(lambda x: any(x.CheckResourceType(i) for i in t), self._rescs)

    def LoadFromFolder(filePath: str, init=True) -> "Graph":
        g = Graph()
        jsonPath = GetJSON(filePath, init)

        data = json.load(open(jsonPath, "r"))
        nodeInvMap:dict[str, Node] = {} 
        # Add all node info
        for node in data["nodes"]:
            newNode = Node(AwsResource, node["data"])
            nodeInvMap[node["data"]["id"]] = newNode
            if newNode.IsVariable():
                g.AddVariable(newNode)
            elif newNode.IsResource():
                g.AddResource(newNode)
            elif newNode.IsOutput():
                g.AddOutput(newNode)

        # Generate connection
        for edge in data["edges"]:
            source = edge["data"]["source"]
            target = edge["data"]["target"]
            nodeInvMap[source].AddToNode(nodeInvMap[target])
            nodeInvMap[target].AddFromNode(nodeInvMap[source])

        return g
