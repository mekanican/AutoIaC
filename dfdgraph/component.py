import graphviz
from typing import List
from utils import get_random_id
from .dataflow import DataFlow

class DFDNode:
    def __init__(self, name):
        self.name = name
        self.id = get_random_id()
        self.dataflow: List[DataFlow] = []
    def DrawNode(g: graphviz.Digraph): # Virtual function
        pass
    def DrawEdge(self, g: graphviz.Digraph):
        for df in self.dataflow:
            df.MakeDirected(g)
    def AddEdge(self, toId: str, label = ""):
        self.dataflow.append(DataFlow(self.id, toId, label))

class DataStore(DFDNode):
    def __init__(self, name=""):
        super().__init__(name)
    def DrawNode(self, g: graphviz.Digraph):
        # g.attr("node", shape="cylinder")
        g.node(self.id, self.name, shape="cylinder")
        pass

class Process(DFDNode):
    def __init__(self, name=""):
        super().__init__(name)
    def DrawNode(self, g: graphviz.Digraph):
        g.node(self.id, self.name, shape="ellipse")

class ExternalEntity(DFDNode):
    def __init__(self, name=""):
        super().__init__(name)
    def DrawNode(self, g: graphviz.Digraph):
        g.node(self.id, self.name, shape="box")