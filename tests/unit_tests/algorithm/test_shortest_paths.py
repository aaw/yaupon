import py.test
import yaupon.algorithm.shortest_path as shortest_path
from yaupon.algorithm.exceptions import NegativeCycleError
from yaupon.tests.testutils import pytest_generate_tests

def populate_test_graph(g):
    for x,y in [(1,2),(2,3),(3,4),(4,5),(5,6),(2,5),(4,10),(10,11),(11,4)]:
        g.add_edge(x,y)  
    g.add_property('edge_weight')
    for e in g.edges():
        g.edge_weight[e] = 1
    for e in g.edges(source=2, target=5):
        g.edge_weight[e] = 10

def test_basic_unweighted(graph):
    populate_test_graph(graph)
    paths_from_1 = shortest_path.compile(graph=graph, source=1)
    path_from_1_to_6 = [(x,y) for x,y in paths_from_1(target=6)]
    assert path_from_1_to_6 == [(1,2), (2,5), (5,6)]
    paths_to_6 = shortest_path.compile(graph=graph, target=6)
    path_to_6_from_1 = [(x,y) for x,y in paths_to_6(source=1)]
    assert path_to_6_from_1 == [(1,2), (2,5), (5,6)]

def test_exhaustive_unweighted(graph):
    populate_test_graph(graph)
    for u in graph.vertices():
        for v in graph.vertices():
            paths_from_u = shortest_path.compile(graph=graph, source=u)
            paths_to_v = shortest_path.compile(graph=graph, target=v)
            u_to_v_from_source = [(x,y) for x,y in paths_from_u(target=v)]
            u_to_v_to_target = [(x,y) for x,y in paths_to_v(source=u)]
            assert u_to_v_from_source == u_to_v_to_target

def test_basic_weighted_no_negative_edges(graph):
    populate_test_graph(graph)
    paths_from_1 = shortest_path.compile(graph=graph, 
                                         source=1,
                                         edge_weight=graph.edge_weight)
    path_from_1_to_6 = [(x,y) for x,y in paths_from_1(target=6)]
    assert path_from_1_to_6 == [(1,2), (2,3), (3,4), (4,5), (5,6)]
    paths_to_6 = shortest_path.compile(graph=graph, 
                                       target=6,
                                       edge_weight=graph.edge_weight)
    path_to_6_from_1 = [(x,y) for x,y in paths_to_6(source=1)]
    assert path_to_6_from_1 == [(1,2), (2,3), (3,4), (4,5), (5,6)]   

def test_exhaustive_weighted_no_negative_edges(graph):
    populate_test_graph(graph)
    for u in graph.vertices():
        for v in graph.vertices():
            paths_from_u = shortest_path.compile(graph=graph, 
                                                 source=u,
                                                 edge_weight=graph.edge_weight)
            paths_to_v = shortest_path.compile(graph=graph, 
                                               target=v,
                                               edge_weight=graph.edge_weight)
            u_to_v_from_source = [(x,y) for x,y in paths_from_u(target=v)]
            u_to_v_to_target = [(x,y) for x,y in paths_to_v(source=u)]
            assert u_to_v_from_source == u_to_v_to_target

def test_basic_weighted_negative_edges(graph):
    populate_test_graph(graph)
    for e in graph.edges(source=3, target=4):
        graph.edge_weight[e] = -5
    paths_from_1 = shortest_path.compile(graph=graph, 
                                         source=1,
                                         edge_weight=graph.edge_weight)
    path_from_1_to_6 = [(x,y) for x,y in paths_from_1(target=6)]
    assert path_from_1_to_6 == [(1,2), (2,3), (3,4), (4,5), (5,6)]
    paths_to_6 = shortest_path.compile(graph=graph, 
                                       target=6,
                                       edge_weight=graph.edge_weight)
    path_to_6_from_1 = [(x,y) for x,y in paths_to_6(source=1)]
    assert path_to_6_from_1 == [(1,2), (2,3), (3,4), (4,5), (5,6)]   

def test_exhaustive_weighted_negative_edges(graph):
    populate_test_graph(graph)
    for e in graph.edges(source=3, target=4):
        graph.edge_weight[e] = -5
    for u in graph.vertices():
        for v in graph.vertices():
            paths_from_u = shortest_path.compile(graph=graph, 
                                                 source=u,
                                                 edge_weight=graph.edge_weight)
            paths_to_v = shortest_path.compile(graph=graph, 
                                               target=v,
                                               edge_weight=graph.edge_weight)
            u_to_v_from_source = [(x,y) for x,y in paths_from_u(target=v)]
            u_to_v_to_target = [(x,y) for x,y in paths_to_v(source=u)]
            assert u_to_v_from_source == u_to_v_to_target

def test_basic_all_pairs(graph):
    populate_test_graph(graph)
    all_paths = shortest_path.compile(graph=graph)
    path_from_1_to_6 = [(x,y) for x,y in all_paths(source=1, target=6)]
    assert path_from_1_to_6 == [(1,2), (2,5), (5,6)]
    path_from_1_to_5 = [(x,y) for x,y in all_paths(source=1, target=5)]
    assert path_from_1_to_5 == [(1,2), (2,5)]
    path_from_2_to_6 = [(x,y) for x,y in all_paths(source=2, target=6)]
    assert path_from_2_to_6 == [(2,5), (5,6)]
    path_from_3_to_4 = [(x,y) for x,y in all_paths(source=3, target=4)]
    assert path_from_3_to_4 == [(3,4)]

def test_exhaustive_all_pairs(graph):
    populate_test_graph(graph)
    all_pairs = shortest_path.compile(graph=graph, 
                                      edge_weight=graph.edge_weight)
    for e in graph.edges(source=3, target=4):
        graph.edge_weight[e] = -5
    for u in graph.vertices():
        for v in graph.vertices():
            paths_from_u = shortest_path.compile(graph=graph, 
                                                 source=u,
                                                 edge_weight=graph.edge_weight)
            paths_to_v = shortest_path.compile(graph=graph, 
                                               target=v,
                                               edge_weight=graph.edge_weight)
            u_to_v_from_source = [(x,y) for x,y in paths_from_u(target=v)]
            u_to_v_to_target = [(x,y) for x,y in paths_to_v(source=u)]
            u_to_v_all_pairs = [(x,y) for x,y in all_pairs(source=u, target=v)]
            assert u_to_v_from_source == u_to_v_to_target
            assert u_to_v_from_source == u_to_v_all_pairs

def test_negative_weight_cycle(graph):
    populate_test_graph(graph)
    # (10,11) is on a cycle, so making its weight small enough makes the 
    # cycle's weight negative

    # -2 isn't small enough, just makes the cycle weight 0
    for edge in graph.edges(source=10, target=11):
        graph.edge_weight[edge] = -2
    shortest_path.compile(graph=graph, edge_weight=graph.edge_weight, source=1)
    
    # -3 is small enough, but we shouldn't throw a NegativeCycleError unless the
    # source is in position to encounter the negative cycle.
    for edge in graph.edges(source=10, target=11):
        graph.edge_weight[edge] = -3
    shortest_path.compile(graph=graph, edge_weight=graph.edge_weight, source=5)
    py.test.raises(NegativeCycleError, 
                   """
                   shortest_path.compile(graph=graph, 
                                         edge_weight=graph.edge_weight,
                                         source=1)
                   """)


