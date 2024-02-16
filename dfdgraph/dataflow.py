import graphviz

class DataFlow:
    def __init__(self, fromId: str, toId: str, label):
        self.fromId = fromId
        self.toId = toId
        self.label = label
    def MakeDirected(self, g: graphviz.Digraph):
        g.edge(self.fromId, self.toId, label=self.label)