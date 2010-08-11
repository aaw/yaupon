from yaupon.util.shortcuts import reverse_edge

class UndirectedGraph(object):
    def __init__(self, graph):
        self.graph = graph
    
    def __getattr__(self, x):
        return getattr(self.graph, x)

    def edges(self, source = None, target = None):
        if source is None and target is None:
            for e in self.graph.edges():
                yield e
        elif source is not None and target is not None:
            for e in self.graph.edges(source=source, target=target):
                yield e
            if source != target:
                for e in self.graph.edges(source=target, target=source):
                    yield e

