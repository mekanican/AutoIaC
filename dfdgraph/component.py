import graphviz
from typing import List, Mapping
from sparta_utils.sparta import SpartaComponent
from utils import get_random_id
from .dataflow import DataFlow

COMPONENT_ID_NODE: Mapping[str, "DFDNode"] = {}

class DFDNode:
    def __init__(self, id, name):
        self.name = name
        if id == "":
            self.id = get_random_id()
        else:
            self.id = str(id)
        COMPONENT_ID_NODE[self.id] = self
        self.dataflow: List[DataFlow] = []
        self.spartaInstance = None
    def DrawNode(self, g: graphviz.Digraph): # Virtual function
        pass
    def Get(self):
        pass
    
    def DrawEdge(self, g: graphviz.Digraph):
        for df in self.dataflow:
            df.MakeDirected(g)
    def AddEdge(self, toNode: "DFDNode", label = "", refBound = None):
        df = DataFlow(self, toNode, label)
        self.dataflow.append(df)
        # Not used!
        if refBound is not None:
            refBound.containedElements.append(df)

class DataStore(DFDNode):
    def __init__(self, id, name=""):
        super().__init__(id, name)
    def DrawNode(self, g: graphviz.Digraph):
        # g.attr("node", shape="cylinder")
        g.node(self.id, self.name, shape="cylinder")
        pass
    def Get(self):
        if self.spartaInstance is None:
            self.spartaInstance = SpartaComponent.DataStore(self.name)
        return self.spartaInstance

class Process(DFDNode):
    def __init__(self, id, name=""):
        super().__init__(id, name)
    def DrawNode(self, g: graphviz.Digraph):
        g.node(self.id, self.name, shape="ellipse")
    def Get(self):
        if self.spartaInstance is None:
            self.spartaInstance = SpartaComponent.Process(self.name)
        return self.spartaInstance

class ExternalEntity(DFDNode):
    def __init__(self, id, name=""):
        super().__init__(id, name)
    def DrawNode(self, g: graphviz.Digraph):
        g.node(self.id, self.name, shape="box")
    def Get(self):
        if self.spartaInstance is None:
            self.spartaInstance = SpartaComponent.ExternalEntity(self.name)
        return self.spartaInstance