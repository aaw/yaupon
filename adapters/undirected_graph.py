from yaupon.util.shortcuts import reverse_edge

class UndirectedGraph(object):
    def __init__(self, graph):
        self.graph = graph
    
    def __getattr__(self, x):
        return getattr(self.graph, x)

    #TODO: this is gross
    def edges(self, source=None, target=None):
        if source is None and target is None:
            for e in self.graph.edges():
                yield e
	        #TODO: still think it might be a good idea to 
                #      yield reverse_edge(e) here, since if you
	        #      really wanted distinct edges, you could
	        #      always get them from any call to edges
	        #      by just filtering distinct edges 
        elif source is not None and target is not None:
            for e in self.graph.edges(source=source, target=target):
                yield e
            if source != target:
                for e in self.graph.edges(source=target, target=source):
                    yield reverse_edge(e)
        elif source is not None:
            for e in self.graph.edges(source=source):
                yield e
            if source != target:
                for e in self.graph.edges(target=source):
                    yield reverse_edge(e)
        else:
            for e in self.graph.edges(target=target):
                yield e
            if source != target:
                for e in self.graph.edges(source=target):
                    yield reverse_edge(e)

