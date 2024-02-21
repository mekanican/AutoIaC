import graphviz

GLOBAL_DF = []

class DataFlow:
    def __init__(self, fromNode, toNode, label):
        self.fromNode = fromNode
        self.toNode = toNode
        self.label = label
        GLOBAL_DF.append(self)
    def MakeDirected(self, g: graphviz.Digraph):
        g.edge(self.fromNode.id, self.toNode.id, label=self.label)