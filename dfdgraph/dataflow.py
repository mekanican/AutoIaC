import graphviz

class DataFlow:
    def __init__(self, fromNode, toNode, label):
        self.fromNode = fromNode
        self.toNode = toNode
        self.label = label
    def MakeDirected(self, g: graphviz.Digraph):
        g.edge(self.fromNode.id, self.toNode.id, label=self.label)