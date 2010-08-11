import yaupon.graph_impl.forest as forest
import yaupon.algorithm.detail.kruskal_minimum_spanning_tree as kruskal

from yaupon.traversal.traversal import traverse
from yaupon.traversal.visitor import TreeFindingVisitor
from yaupon.traversal.generators import depth_first_generator
from yaupon.util.shortcuts import other_vertex, reverse_edge
from yaupon.adapters.reversed_graph import ReversedGraph


class mst(object):
    def __init__(self, description):
        self.description = description

    def compile(self, graph, edge_weight=None):
        initial_vertex = graph.vertices().__iter__().next()
        if self.description == 'depth_first_search':
            self.tree = traverse([initial_vertex],
                                 TreeFindingVisitor(),
                                 depth_first_generator(graph))
        elif self.description == 'kruskal':
            self.forest = forest.Forest()
            for edge in kruskal.spanning_tree_edges(graph=graph,
                                                    edge_weight=edge_weight):
                self.forest.add_edge(*edge)

    def __call__(self, source, target):
        for edge in self.forest.path(source, target):
            yield edge

def compile(graph, edge_weight=None):
    if edge_weight is None:
        algorithm = mst('depth_first_search')
        algorithm.compile(graph=graph)
    else:
        algorithm = mst('kruskal')
        algorithm.compile(graph=graph, edge_weight=edge_weight)
    return algorithm

