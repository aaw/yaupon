from yaupon.util.shortcuts import reverse_edge

class ReversedGraph(object):
    def __init__(self, graph):
        self.graph = graph
    
    def __getattr__(self, x):
        return getattr(self.graph, x)

    def edges(self, source = None, target = None):
        for e in self.graph.edges(source=target, target=source):
            yield reverse_edge(e)
