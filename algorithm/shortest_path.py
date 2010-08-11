import yaupon.algorithm.detail.dijkstra_shortest_path as dijkstra
import yaupon.algorithm.detail.bellman_ford_shortest_path as bellman_ford

from yaupon.traversal.traversal import traverse
from yaupon.traversal.aggregate_visitor import AggregateVisitor, ParentEdge
from yaupon.traversal.generators import breadth_first_generator
from yaupon.util.shortcuts import other_vertex, reverse_edge
from yaupon.adapters.reversed_graph import ReversedGraph


class single_source(object):
    def __init__(self, description):
        self.description = description

    def compile(self, graph, edge_weight=None, source=None, target=None):
        if target is not None:
            graph = ReversedGraph(graph)
            self.tree_type = 'from_target'
            self.initial_vertex = target
        else:
            self.tree_type = 'from_source'
            self.initial_vertex = source

        if self.description == 'breadth_first_search':
            v = AggregateVisitor(visitors=[ParentEdge], backend=graph)
            traverse(root_vertices=[self.initial_vertex],
                     visitor=v,
                     generator=breadth_first_generator(graph))
            self.tree = v.ParentEdge
        elif self.description == 'dijkstra':
            self.tree = dijkstra.make_tree(graph, source=self.initial_vertex,
                                           edge_weight=edge_weight)
        elif self.description == 'bellman_ford':
            self.tree = bellman_ford.make_tree(graph,
                                               source=self.initial_vertex,
                                               edge_weight=edge_weight)

    def __call__(self, **kwargs):
        if self.tree_type == 'from_source':
            v = kwargs['target']
        else:
            v = kwargs['source']

        #TODO: simplify this mess
        edges = [] 
        while self.tree.get(v) is not None:
            edges.append(self.tree[v])
            v = other_vertex(self.tree[v], v)
        if self.tree_type == 'from_source':
            for e in reversed(edges):
                yield e
        else:
            for e in edges:
                yield reverse_edge(e)

class single_source_collection(object):
    def __init__(self):
        self.description = 'all_pairs_lazy_evaluated'
        self.single_source_cache = {}

    def compile(self, graph, edge_weight=None):
        self.graph = graph
        self.edge_weight = edge_weight

    def __call__(self, source, target):
        cached = self.single_source_cache.get(source)
        if cached is None:
            cached = compile(self.graph, self.edge_weight, source)
            self.single_source_cache[source] = cached
        return cached(source=source, target=target) 

def compile(graph, edge_weight=None, source=None, target=None):
    if source is None and target is None:
        algorithm = single_source_collection()
        algorithm.compile(graph=graph, edge_weight=edge_weight)
    elif edge_weight is None:
        algorithm = single_source('breadth_first_search')
        algorithm.compile(graph=graph, source=source, target=target)
    else:
        #single source (or single target == graph reversed
        # first, test for a negative edge weight
        if any(edge_weight[e] < 0 for e in graph.edges()):
            algorithm = single_source('bellman_ford')
        else:
            algorithm = single_source('dijkstra')
        algorithm.compile(graph=graph, source=source, target=target,
                          edge_weight=edge_weight)
    return algorithm

