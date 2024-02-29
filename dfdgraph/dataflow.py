import graphviz

from sparta_utils.sparta import SpartaComponent

GLOBAL_DF = []
GLOBAL_DF_SP = []

class DataFlow:
    def __init__(self, fromNode, toNode, label):
        self.fromNode = fromNode
        self.toNode = toNode
        self.label = label
        self.df = SpartaComponent.DataFlow(self.fromNode.Get(), self.toNode.Get())
        GLOBAL_DF.append(self)
        GLOBAL_DF_SP.append(self.df)
        
    def MakeDirected(self, g: graphviz.Digraph):
        g.edge(self.fromNode.id, self.toNode.id, label=self.label)
    def Get(self):
        return self.df