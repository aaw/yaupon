from yaupon.data_structures import ydeque, ydict
from yaupon.traversal import *

# A composite visitor implementing the Cheriyan-Mehlhorn/Gabow
# strongly connected components algorithm
class ConnectedComponents(CompositeVisitor):
    dependencies = [DiscoverTime]

    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)
        self.S = ydeque(backend=agg)
        self.P = ydeque(backend=agg)
        self.next_component_id = 0

    def discover_vertex(self, v):
        self.S.append(v)
        self.P.append(v)

    def back_edge(self, e):
        v,w = e
        if self.value.get(w) is not None:
            return

        while self.properties.DiscoverTime[self.P[-1]] > \
              self.properties.DiscoverTime[w]:
            self.P.pop()

    def finish_vertex(self, v):
        if v == self.P[-1]:
            while self.value.get(v) is None:
                self.value[self.S.pop()] = self.next_component_id
            self.P.pop()
            self.next_component_id += 1

class StronglyConnectedComponents(object):
    def __init__(self, graph):
        self.description = \
            'Cheriyan-Mehlhorn/Gabow strongly-connected components'
        generator = depth_first_generator(graph)
        visitor = AggregateVisitor(backend=graph, 
                                   visitors={ConnectedComponents:None}) 
        traverse(root_vertices=graph.vertices(),
                 visitor=visitor,
                 generator=depth_first_generator(graph))
        self.components = visitor.ConnectedComponents

    def __call__(self, v):
        return self.components[v]

def compile(graph):
    return StronglyConnectedComponents(graph)

