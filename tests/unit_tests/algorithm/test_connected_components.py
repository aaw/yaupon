import py.test
import yaupon.algorithm.connected_components as connected_components
from yaupon.tests.testutils import pytest_generate_tests

def test_all_unique_components(graph):
    for v in xrange(100):
        graph.add_vertex()
    components = connected_components.compile(graph)
    recorded_components = set()
    for v in graph.vertices():
        recorded_components.add(components(v))
    assert len(recorded_components) == sum(1 for v in graph.vertices())

def test_straight_line(graph):
    for i in xrange(20):
        graph.add_edge(i,i+1)
    components = connected_components.compile(graph)
    recorded_components = set()
    for v in graph.vertices():
        recorded_components.add(components(v))
    assert len(recorded_components) == sum(1 for v in graph.vertices())

def test_undirected_straight_line(graph):
    #TODO: would be nice to have some generators for common graphs,
    #      so that I could just say line_graph here...
    for i in xrange(20):
        graph.add_edge(i,i+1)
        graph.add_edge(i+1,i)
    components = connected_components.compile(graph)
    recorded_components = set()
    for v in graph.vertices():
        recorded_components.add(components(v))
    assert len(recorded_components) == 1

def test_simple_graph(graph):
    # A simple example of strongly connected components
    graph.add_edge('a','b')
    graph.add_edge('b','c')
    graph.add_edge('c','b')
    graph.add_edge('c','d')
    graph.add_edge('d','b')
    graph.add_edge('d','e')
    components = connected_components.compile(graph)
    assert len(set([components('a'), components('b'), components('e')])) == 3
    assert components('b') == components('c')
    assert components('c') == components('d')

