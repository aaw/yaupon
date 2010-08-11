from yaupon.tests.testutils import graph_database_iteration
from yaupon.traversal import *
from yaupon.adapters.undirected_graph import UndirectedGraph
import yaupon.algorithm.shortest_path as shortest_path


def pytest_generate_tests(metafunc):
    graph_database_iteration(metafunc)

def test_every_vertex_discovered(graph):
    g = graph()
    visitor = AggregateVisitor(visitors=[DiscoverTime])
    traverse(g.vertices(), visitor, depth_first_generator(g))
    discover_times = set()
    for v in g.vertices():
        assert visitor.DiscoverTime[v] not in discover_times
        discover_times.add(visitor.DiscoverTime[v])
    #assert that the discover times form a contiguous range
    prev = min(visitor.DiscoverTime[v] for v in g.vertices()) - 1
    for t in sorted(visitor.DiscoverTime[v] for v in g.vertices()):
        assert t - prev == 1
        prev = t

def test_graph_splits(graph):
    """
    In any depth-first search tree, any edge (root, X) in
    the depth-first search tree partitions the graph: there
    are no edges from any vertex visited before X to any
    vertices visited after X in the original graph.
    """
    g = graph()
    visitor = AggregateVisitor(visitors=[Parent, ParentEdge, DiscoverTime])
    traverse(g.vertices(), visitor, depth_first_generator(g))
    root = [v for v,time in visitor.DiscoverTime.iteritems() if time == 0][0]
    root_edges = [visitor.ParentEdge[v] for v in g.vertices() \
                  if v != root and visitor.Parent[v] == root] 
    for x,y in root_edges:
        before = [v for v in g.vertices() \
                  if visitor.DiscoverTime[v] < visitor.DiscoverTime[y] and \
                     v != root]
        after = [v for v in g.vertices() \
                 if visitor.DiscoverTime[v] > visitor.DiscoverTime[y]]
        for b in before:
            for a in after:
                assert [e for e in g.edges(source=b, target=a)] == []


def test_graph_splits_undirected(graph):
    """
    In any depth-first search tree of an undirected graph, any 
    edge (root, X) in the depth-first search tree partitions 
    the graph: there are no edges between any vertex visited 
    before X and any vertices visited after X in the original graph.
    """
    g = UndirectedGraph(graph())
    visitor = AggregateVisitor(visitors=[Parent, ParentEdge, DiscoverTime])
    traverse(g.vertices(), visitor, depth_first_generator(g))
    root = [v for v,time in visitor.DiscoverTime.iteritems() if time == 0][0]
    root_edges = [visitor.ParentEdge[v] for v in g.vertices() \
                  if v != root and visitor.Parent[v] == root] 
    for x,y in root_edges:
        before = [v for v in g.vertices() \
                  if visitor.DiscoverTime[v] < visitor.DiscoverTime[y] \
                  and v != root]
        after = [v for v in g.vertices() \
                 if visitor.DiscoverTime[v] > visitor.DiscoverTime[y]]
        for b in before:
            for a in after:
                assert [e for e in g.edges(source=b, target=a)] == []
                assert [e for e in g.edges(source=a, target=b)] == []
