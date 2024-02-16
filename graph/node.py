from typing import List, Type
from annotation import ResourceName
from annotation import BlockType

class Node:
    def __init__(self, provider: List[Type], kvargs: dict[str, str]):
        self.module = Node.ParseModule(kvargs["id"])
        self.parent = kvargs.get("parent", "")
        self.label = kvargs["label"]
        self.type = BlockType(kvargs["type"])
        self.fromNodes:List[Node] = []
        self.toNodes:List[Node] = []
        # Resource labeling
        resourceType = self.label.split(".")[0]
        self.rescType = None
        for prd in provider:
            try:
                self.rescType = prd(resourceType)
            except:
                continue
    
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
        return self.type == BlockType.VARIABLE
    def IsResource(self):
        return self.type == BlockType.RESOURCE
    def IsOutput(self):
        return self.type == BlockType.OUTPUT

    def CheckResourceType(self, t: ResourceName):
        return self.rescType == t