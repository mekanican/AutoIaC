import graphviz
from typing import List
from .component import DFDNode, ExternalEntity
from .trustboundary import TrustBoundary

class Diagram:
    def __init__(self):
        self.publicNodes: List[DFDNode] = []
        self.boundaries: List[TrustBoundary] = []

    def DrawDiagram(self, g: graphviz.Digraph):
        # Special node representates User
        user = ExternalEntity("User")
        # Connect to all public node
        # !TODO: Assume User has bidirectional data flow to those node
        for node in self.publicNodes:
            user.AddEdge(node.id)
            node.AddEdge(user.id)

        # Separating node and edge draw (graphviz bug)
        user.DrawNode(g)
        for bound in self.boundaries:
            bound.DrawBoundNode(g)

        user.DrawEdge(g)
        for bound in self.boundaries:
            bound.DrawBoundEdge(g)

    def AddPublicNode(self, n: DFDNode):
        self.publicNodes.append(n)
    def AddBoundary(self, b: TrustBoundary):
        self.boundaries.append(b)