import graphviz
from typing import List

from sparta_utils.sparta import SpartaComponent
from .component import DFDNode

class TrustBoundary:
    boundaryIdx = 0
    def __init__(self, name = ""):
        self.name = name
        self.nodes: List[DFDNode] = []
        self.innerBoundaries: List[TrustBoundary] = []

        self.spartaBoundary = SpartaComponent.TrustBoundaryContainer(name)

        # self.g:graphviz.Digraph = g.subgraph(name=f"cluster_{TrustBoundary.boundaryIdx}")
        self.currentIdx = TrustBoundary.boundaryIdx
        TrustBoundary.boundaryIdx += 1
    def DrawBoundNode(self,g: graphviz.Digraph):
        with g.subgraph(name=f"cluster_{self.currentIdx}") as sg:
            sg.attr(style="dashed", color="firebrick2")
            sg.attr(label=self.name)
            for node in self.nodes:
                node.DrawNode(sg)
                # node.DrawEdge(sg)
            for boundary in self.innerBoundaries:
                boundary.DrawBoundNode(sg)
    def DrawBoundEdge(self, g:graphviz.Digraph):
        for node in self.nodes:
            node.DrawEdge(g)
        for boundary in self.innerBoundaries:
            boundary.DrawBoundEdge(g)
    def AddNode(self, n: DFDNode):
        self.nodes.append(n)
        self.spartaBoundary.containedElements.append(n.Get())

    def Get(self):
        return self.spartaBoundary

    def AddInnerBound(self, bound: "TrustBoundary"):
        self.innerBoundaries.append(bound)
        self.spartaBoundary.containedElements.append(bound.Get())