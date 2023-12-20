import graphviz
from typing import *
from random import choices
from string import ascii_lowercase

class DFDNode:
    def __init__(self, name):
        self.name = name
        self.id = ''.join(choices(ascii_lowercase, k=10))
        self.dataflow: List[DataFlow] = []
    def DrawNode(g: graphviz.Digraph):
        pass
    def DrawEdge(self, g: graphviz.Digraph):
        for df in self.dataflow:
            df.MakeDirected(g)
    def AddEdge(self, toId: str, label = ""):
        self.dataflow.append(DataFlow(self.id, toId, label))

class DataFlow:
    def __init__(self, fromId: str, toId: str, label):
        self.fromId = fromId
        self.toId = toId
        self.label = label
    def MakeDirected(self, g: graphviz.Digraph):
        g.edge(self.fromId, self.toId, label=self.label)

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

class TrustBoundary:
    boundaryIdx = 0
    def __init__(self, name = ""):
        self.name = name
        self.nodes: List[DFDNode] = []
        self.innerBoundaries: List[TrustBoundary] = []

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

    def AddInnerBound(self, bound: "TrustBoundary"):
        self.innerBoundaries.append(bound)


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



if __name__ == "__main__":
    print("Helloworld")
    g = graphviz.Digraph("G", filename="magic.dot")

    diag = Diagram()
    tb = TrustBoundary("Trust 1")
    common = TrustBoundary("Common")
    common.AddInnerBound(tb)
    a = Process("A")
    common.AddNode(a)

    diag.AddBoundary(common)
    diag.AddPublicNode(a)

    b = DataStore("B")
    c = ExternalEntity("C")
    tb.AddNode(b)
    tb.AddNode(c)

    a.AddEdge(b.id)
    b.AddEdge(c.id)
    diag.DrawDiagram(g)
    g.render(view=False)