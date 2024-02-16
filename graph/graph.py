from typing import List
from os import environ
from annotation import ResourceName, AwsResource
from .node import Node
import json

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
        """Load Terraform project to Directed Graph

        Args:
            filePath (str): Path to terraform project
            init (bool, optional): Should project be re-initiated. Defaults to True.

        Returns:
            Graph: _description_
        """        
        from tfparser import GetJSON
        g = Graph()
        jsonPath = GetJSON(filePath, init, environ.get("TOFU", "") != "") # Automatically detect based on commandline

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

        data = json.load(open(jsonPath, "r"))
        nodeInvMap:dict[str, Node] = {} 
        # Add all node info
        for node in data["nodes"]:
            # TODO: Create Option for specify list of provider
            newNode = Node([AwsResource], node["data"])
            nodeInvMap[node["data"]["id"]] = newNode
            if newNode.IsVariable():
                g.AddVariable(newNode)
            elif newNode.IsResource():
                g.AddResource(newNode)
            elif newNode.IsOutput():
                g.AddOutput(newNode)

        
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

        # Generate connection
        for edge in data["edges"]:
            source = edge["data"]["source"]
            target = edge["data"]["target"]
            nodeInvMap[source].AddToNode(nodeInvMap[target])
            nodeInvMap[target].AddFromNode(nodeInvMap[source])

        return g
