from yaupon.tests.testutils import graph_database_iteration
from yaupon.traversal import *
from yaupon.adapters.undirected_graph import UndirectedGraph
import yaupon.algorithm.shortest_path as shortest_path


def pytest_generate_tests(metafunc):
    graph_database_iteration(metafunc)

def test_bfs_properties(graph):
    """
    In any breadth-first search tree, all edges either (1) are in the
    tree, (2) connect two vertices in the same level of the tree, or
    (3) connect two vertices from adjacent levels of the tree
    """
    g = graph()
    visitor = AggregateVisitor(visitors=[ParentEdge, Depth])
    traverse(g.vertices(), visitor, breadth_first_generator(g))
    tree_edges = set([e for e in visitor.ParentEdge.itervalues() \
                      if e is not None])
    for e in g.edges():
        if e not in tree_edges:
            u_depth = visitor.Depth[e[0]]
            v_depth = visitor.Depth[e[1]]
            if u_depth < v_depth:
                assert v_depth - u_depth == 1

def test_bfs_properties_undirected(graph):
    """
    In any breadth-first search tree, all edges either (1) are in the
    tree, (2) connect two vertices in the same level of the tree, or
    (3) connect two vertices from adjacent levels of the tree
    """
    g = UndirectedGraph(graph())
    visitor = AggregateVisitor(visitors=[ParentEdge, Depth])
    traverse(g.vertices(), visitor, breadth_first_generator(g))
    tree_edges = set([e for e in visitor.ParentEdge.itervalues() \
                      if e is not None])
    for e in g.edges():
        if e not in tree_edges:
            u_depth = visitor.Depth[e[0]]
            v_depth = visitor.Depth[e[1]]
            assert u_depth == v_depth or abs(u_depth - v_depth) == 1

