from yaupon.adapters.reversed_graph import ReversedGraph
from yaupon.tests.testutils import pytest_generate_tests

def test_all_edges(graph):
    graph.add_edge(1,2)
    graph.add_edge('a','a')
    graph.add_edge(1,3)
    graph.add_edge(3,1)
    graph.add_edge(4,'b')
    r = ReversedGraph(graph)    
    assert sorted([(s,t) for s,t in r.edges()]) == \
           sorted([(2,1), ('a','a'), (1,3), (3,1), ('b',4)])
    rr = ReversedGraph(r)
    assert sorted([(s,t) for s,t in rr.edges()]) == \
           sorted([(s,t) for s,t in graph.edges()])

def test_edges_by_source(graph):
    graph.add_edge(1,2)
    graph.add_edge('a','a')
    graph.add_edge(1,3)
    graph.add_edge(3,1)
    graph.add_edge(4,'b')
    graph.add_edge(4,'b')
    r = ReversedGraph(graph)
    assert [(s,t) for s,t in r.edges(source=1)] == [(1,3)]
    assert [(s,t) for s,t in r.edges(source=2)] == [(2,1)]
    assert [(s,t) for s,t in r.edges(source=3)] == [(3,1)]
    assert [(s,t) for s,t in r.edges(source='a')] == [('a','a')]
    assert [(s,t) for s,t in r.edges(source='b')] == [('b',4), ('b',4)]
    assert [(s,t) for s,t in r.edges(source=4)] == []

def test_edges_by_target(graph):
    graph.add_edge(1,2)
    graph.add_edge('a','a')
    graph.add_edge(1,3)
    graph.add_edge(3,1)
    graph.add_edge(4,'b')
    graph.add_edge(4,'b')
    r = ReversedGraph(graph)
    assert sorted([(s,t) for s,t in r.edges(target=1)]) == \
           sorted([(2,1), (3,1)])
    assert [(s,t) for s,t in r.edges(target=3)] == [(1,3)]
    assert [(s,t) for s,t in r.edges(target=4)] == [('b',4), ('b',4)]
    assert [(s,t) for s,t in r.edges(target='a')] == [('a','a')]
    assert [(s,t) for s,t in r.edges(target='b')] == []

def test_edges_by_source_and_target(graph):
    graph.add_edge(1,2)
    graph.add_edge('a','a')
    graph.add_edge(1,3)
    graph.add_edge(3,1)
    graph.add_edge(4,'b')
    graph.add_edge(4,'b')
    r = ReversedGraph(graph)
    assert [(s,t) for s,t in r.edges(source=2, target=1)] == [(2,1)]
    assert [(s,t) for s,t in r.edges(source='a', target='a')] == [('a','a')]
    assert [(s,t) for s,t in r.edges(source=1, target=3)] == [(1,3)]
    assert [(s,t) for s,t in r.edges(source=3, target=1)] == [(3,1)]
    assert [(s,t) for s,t in r.edges(source='b', target=4)] == \
           [('b',4), ('b',4)]
    assert [(s,t) for s,t in r.edges(source=4, target='b')] == []
