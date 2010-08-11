import itertools
import py.test

from yaupon.tests.testutils import pytest_generate_tests
import yaupon.graph_impl.exceptions as exceptions

def count_iterable(iterable):
    return sum(1 for x in iterable)

def test_vertices(graph):
    assert [v for v in graph.vertices()] == []
    assert graph.add_vertex('NYC') == 'NYC'
    assert graph.add_vertex('BOS') == 'BOS'
    assert graph.add_vertex('LAX') == 'LAX'
    # if a vertex is added more than once, it's ignored. this allows
    # you to do stuff like g.add_edge(0,1)
    # which adds (0,1) whether or not 0 and 1 exist in the graph
    assert graph.add_vertex('NYC') == 'NYC'
    assert sorted(graph.vertices()) == ['BOS','LAX','NYC']
    assert graph.add_vertex(1) == 1
    v = graph.add_vertex()
    graph.add_vertex(v) # no effect
    graph.add_vertex(v) # no effect
    graph.add_vertex('NYC') # no effect
    
    assert v in graph.vertices()
    assert 1 in graph.vertices()
    assert 'NYC' in graph.vertices()
    assert 'BOS' in graph.vertices()
    assert 'LAX' in graph.vertices()
    assert count_iterable(graph.vertices()) == 5

    graph.remove_vertex('NYC')
    assert 'NYC' not in graph.vertices()
    assert count_iterable(graph.vertices()) == 4

    graph.remove_vertex(v)
    assert v not in graph.vertices()
    assert count_iterable(graph.vertices()) == 3

def test_edges(graph):
    assert [e for e in graph.edges()] == []
    u = graph.add_vertex()
    v = graph.add_vertex('hello')
    x = graph.add_vertex('world')
    y = graph.add_vertex(123.22)
    u_v = graph.add_edge(u,v)
    v_x = graph.add_edge(v,x)
    x_v = graph.add_edge(x,v)
    u_y = graph.add_edge(u,y)
    u_y2 = graph.add_edge(u,y)
    y_y = graph.add_edge(y,y)

    # Sanity checks
    assert count_iterable(graph.edges()) == 6
    assert u_v != v_x
    assert v_x != x_v
    assert u_y != u_y2
    
    # Test a specified source
    assert sorted(graph.edges(source = u)) == sorted([u_v,u_y,u_y2])
    assert sorted(graph.edges(source = v)) == [v_x]
    assert sorted(graph.edges(source = x)) == [x_v]
    assert sorted(graph.edges(source = y)) == [y_y]
    
    # Test a specified target
    assert sorted(graph.edges(target = u)) == []
    assert sorted(graph.edges(target = v)) == sorted([u_v,x_v])
    assert sorted(graph.edges(target = x)) == [v_x]
    assert sorted(graph.edges(target = y)) == sorted([u_y,y_y,u_y2])

    # Test a specified edge
    assert sorted(graph.edges(source = u, target = v)) == [u_v]
    assert sorted(graph.edges(source = v, target = x)) == [v_x]
    assert sorted(graph.edges(source = x, target = v)) == [x_v]
    assert sorted(graph.edges(source = u, target = y)) == sorted([u_y,u_y2])
    assert sorted(graph.edges(source = y, target = y)) == [y_y]
    assert sorted(graph.edges(source = x, target = y)) == []
    assert sorted(graph.edges(source = y, target = x)) == []

def test_add_edge_unknown_vertex(graph):
    graph.add_vertex('KNOWN')
    graph.add_edge('KNOWN', 'UNKNOWN')
    graph.add_edge('UNKNOWN', 'KNOWN')
    assert sorted(graph.vertices()) == sorted(['KNOWN', 'UNKNOWN'])
    assert sorted((x,y) for x,y in graph.edges()) == \
           sorted([('KNOWN', 'UNKNOWN'), ('UNKNOWN', 'KNOWN')])
    
def test_remove_vertex(graph):
    for v in 'ABCDEF':
        graph.add_vertex(v)
    ab = graph.add_edge('A','B')
    bc = graph.add_edge('B','C')
    cd = graph.add_edge('C','D')
    de = graph.add_edge('D','E')
    ef = graph.add_edge('E','F')
    fa = graph.add_edge('F','A')

    graph.remove_vertex('D')
    assert sorted(graph.vertices()) == sorted(['A','B','C','E','F'])
    assert sorted(graph.edges()) == sorted([ab,bc,ef,fa])
    graph.remove_vertex('B')
    assert sorted(graph.vertices()) == sorted(['A','C','E','F'])
    assert sorted(graph.edges()) == sorted([ef,fa])
    graph.remove_vertex('F')
    assert sorted(graph.vertices()) == sorted(['A','C','E'])
    assert sorted(graph.edges()) == sorted([])

def test_remove_vertex_unknown(graph):
    py.test.raises(exceptions.VertexNotFoundError, 
                   "graph.remove_vertex('A')")    

def test_remove_edge(graph):
    edges = []
    for i in xrange(10):
        for j in xrange(10):
            edges.append(graph.add_edge(i,j))
    while edges:
        graph.remove_edge(edges[-1])
        edges.pop()
        assert sorted(graph.edges()) == sorted(edges)

def test_construct_with_vertex_list(graph_type):
    g1 = graph_type(vertices = xrange(10))
    g2 = graph_type()
    for i in xrange(10):
        g2.add_vertex(i)
    assert sorted(g1.vertices()) == sorted(g2.vertices())
    assert sorted(g1.edges()) == sorted(g2.edges())

def test_construct_with_edge_list(graph_type):
    edge_list = [(0,1),(2,3),(4,4),(3,0)]
    g1 = graph_type(edges = edge_list)
    g2 = graph_type()
    for e in edge_list:
        for v in e:
            g2.add_vertex(v)
    for u,v in edge_list:
        g2.add_edge(u,v)
    g3 = graph_type()
    for u,v in edge_list:
        g3.add_edge(g3.add_vertex(u), g3.add_vertex(v))
    assert sorted(g1.vertices()) == sorted(g2.vertices())
    assert sorted(g1.vertices()) == sorted(g3.vertices())
    assert sorted([(x,y) for x,y in g1.edges()]) == \
           sorted([(x,y) for x,y in g2.edges()])
    assert sorted([(x,y) for x,y in g1.edges()]) == \
           sorted([(x,y) for x,y in g3.edges()])

def test_construct_with_vertex_and_edge_list(graph_type):
    edge_list = [(0,1),(3,4),(4,0),(5,5),(4,0)]
    g1 = graph_type(vertices = xrange(10), edges = edge_list)
    g2 = graph_type(vertices = xrange(10))
    for x,y in edge_list:
        g2.add_edge(x,y)
    g3 = graph_type()
    for x in xrange(10):
        g3.add_vertex(x)
    for x,y in edge_list:
        g3.add_edge(x,y)
    assert sorted(g1.vertices()) == sorted(g2.vertices())
    assert sorted(g1.vertices()) == sorted(g3.vertices())
    assert sorted([(x,y) for x,y in g1.edges()]) == \
           sorted([(x,y) for x,y in g2.edges()])
    assert sorted([(x,y) for x,y in g1.edges()]) == \
           sorted([(x,y) for x,y in g3.edges()])

def test_property_get(graph):
    for u,v in [('a','b'),('b','b'),('c','a')]:
        graph.add_edge(u,v)
    graph.add_property('vertex_name')
    graph.add_property('edge_weight')
    for v in graph.vertices():
        assert graph.vertex_name.get(v) is None
    for e in graph.edges():
        assert graph.edge_weight.get(e) is None
    e,f,g = graph.edges()
    graph.vertex_name['a'] = 'vertex a'
    graph.edge_weight[e] = 1
    graph.edge_weight[g] = 1
    assert graph.vertex_name.get('a') == 'vertex a'
    assert graph.vertex_name.get('b') is None
    assert graph.vertex_name.get('c') is None
    assert graph.edge_weight.get(e) == 1
    assert graph.edge_weight.get(f) is None
    assert graph.edge_weight.get(g) == 1

def test_make_internal_property(graph):
    for u,v in [('a','b'),('c','d')]:
        graph.add_edge(u,v)
    graph.add_property('vertex_name')
    graph.add_property('edge_weight')
    assert sorted(graph.properties().keys()) == \
           sorted(['edge_weight','vertex_name'])
    graph.vertex_name['a'] = 1
    graph.vertex_name['b'] = 2
    graph.vertex_name['c'] = 3
    graph.vertex_name['d'] = 4
    e,f = graph.edges()
    graph.edge_weight[e] = 11
    graph.edge_weight[f] = 34
    assert graph.vertex_name['a'] == 1
    assert graph.vertex_name['b'] == 2
    assert graph.edge_weight[e] == 11
    assert graph.edge_weight[f] == 34
    for v in graph.vertices():
        assert graph.vertex_name[v] == graph.properties()['vertex_name'][v]
    for e in graph.edges():
        assert graph.edge_weight[e] == graph.properties()['edge_weight'][e]
    graph.remove_property('vertex_name')
    assert graph.properties().keys() == ['edge_weight']
    graph.remove_property('edge_weight')
    assert graph.properties().keys() == []

def test_no_global_iterator_state_kept(graph):
    graph.add_edge(0,1)
    graph.add_edge(1,2)
    graph.add_edge(2,3)
    v_iter = graph.vertices()
    all_vertices = [v for v in graph.vertices()]
    first_vertex = graph.vertices().next()
    assert sorted(v_iter) == sorted(all_vertices)
    e_iter = graph.edges()
    all_edges = [e for e in graph.edges()]
    first_edge = graph.edges().next()
    assert sorted(e_iter) == sorted(all_edges)
    e_source_iter = graph.edges(source=0)
    all_source_edges = [e for e in graph.edges(source=0)]
    first_source_edge = graph.edges(source=0).next()
    assert sorted(e_source_iter) == sorted(all_source_edges)
    e_target_iter = graph.edges(target=3)
    all_target_edges = [e for e in graph.edges(target=3)]
    first_target_edge = graph.edges(target=3).next()
    assert sorted(e_target_iter) == sorted(all_target_edges)
    e_one_iter = graph.edges(source=1,target=2)
    all_one_edges = [e for e in graph.edges(source=1,target=2)]
    first_one_edge = graph.edges(source=1,target=2).next()
    assert sorted(e_one_iter) == sorted(all_one_edges)
