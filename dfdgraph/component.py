import graphviz
from typing import List
from sparta_utils.sparta import SpartaComponent
from utils import get_random_id
from .dataflow import DataFlow

class DFDNode:
    def __init__(self, name):
        self.name = name
        self.id = get_random_id()
        self.dataflow: List[DataFlow] = []
        self.spartaInstance = None
    def DrawNode(self, g: graphviz.Digraph): # Virtual function
        pass
    def Get(self):
        pass
    
    def DrawEdge(self, g: graphviz.Digraph):
        for df in self.dataflow:
            df.MakeDirected(g)
    def AddEdge(self, toNode: "DFDNode", label = ""):
        self.dataflow.append(DataFlow(self, toNode, label))

class DataStore(DFDNode):
    def __init__(self, name=""):
        super().__init__(name)
    def DrawNode(self, g: graphviz.Digraph):
        # g.attr("node", shape="cylinder")
        g.node(self.id, self.name, shape="cylinder")
        pass
    def Get(self):
        if self.spartaInstance is None:
            self.spartaInstance = SpartaComponent.DataStore(self.name)
        return self.spartaInstance

class Process(DFDNode):
    def __init__(self, name=""):
        super().__init__(name)
    def DrawNode(self, g: graphviz.Digraph):
        g.node(self.id, self.name, shape="ellipse")
    def Get(self):
        if self.spartaInstance is None:
            self.spartaInstance = SpartaComponent.Process(self.name)
        return self.spartaInstance

class ExternalEntity(DFDNode):
    def __init__(self, name=""):
        super().__init__(name)
    def DrawNode(self, g: graphviz.Digraph):
        g.node(self.id, self.name, shape="box")
    def Get(self):
        if self.spartaInstance is None:
            self.spartaInstance = SpartaComponent.ExternalEntity(self.name)
        return self.spartaInstance