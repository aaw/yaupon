import itertools
import py.test

from yaupon.tests.testutils import pytest_generate_tests
import yaupon.graph_impl.exceptions as exceptions

def test_vertices(forest):
    assert [v for v in forest.vertices()] == []
    assert forest.add_vertex('NYC') == 'NYC'
    assert forest.add_vertex('BOS') == 'BOS'
    assert forest.add_vertex('LAX') == 'LAX'
    # if a vertex is added more than once, it's ignored. this allows
    # you to do stuff like forest.add_edge(0,1)
    # which adds (0,1) whether or not 0 and 1 exist in the graph
    assert forest.add_vertex('NYC') == 'NYC'
    assert sorted(forest.vertices()) == ['BOS','LAX','NYC']
    assert forest.add_vertex(1) == 1
    v = forest.add_vertex()
    forest.add_vertex(v) # no effect
    forest.add_vertex(v) # no effect
    forest.add_vertex('NYC') # no effect
    
    assert v in forest.vertices()
    assert 1 in forest.vertices()
    assert 'NYC' in forest.vertices()
    assert 'BOS' in forest.vertices()
    assert 'LAX' in forest.vertices()
    assert sum(1 for v in forest.vertices()) == 5

    forest.remove_vertex('NYC')
    assert 'NYC' not in forest.vertices()
    assert sum(1 for v in forest.vertices()) == 4

    forest.remove_vertex(v)
    assert v not in forest.vertices()
    assert sum(1 for v in forest.vertices()) == 3

def test_basic_edges(forest):
    edges_to_add = [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]
    edges_added = []
    for x,y in edges_to_add:
        edges_added.append(forest.add_edge(x,y))
    assert sorted((x,y) for x,y in edges_added) == sorted(edges_to_add)
    assert sorted((x,y) for x,y in forest.edges()) == sorted(edges_to_add)
    for p in xrange(7):
        assert sorted([(x,y) for x,y in forest.edges(parent=p)]) == \
               sorted([(x,y) for x,y in edges_to_add if x == p])
    for c in xrange(7):
        assert sorted([(x,y) for x,y in forest.edges(child=c)]) == \
               sorted([(x,y) for x,y in edges_to_add if y == c])
        assert len([e for e in forest.edges(child=c)]) <= 1

def test_edges_reversed(forest):
    edges_to_add = [(6,2),(5,2),(4,1),(3,1),(2,0),(1,0)]
    for x,y in edges_to_add:
        forest.add_edge(x,y)
    # if we rereoot at 0, we should have the same tree used in
    # test_basic_edges
    forest.reroot(0)
    edges_to_add = [(y,x) for x,y in edges_to_add]

    assert sorted((x,y) for x,y in forest.edges()) == sorted(edges_to_add)
    for p in xrange(7):
        assert sorted([(x,y) for x,y in forest.edges(parent=p)]) == \
               sorted([(x,y) for x,y in edges_to_add if x == p])
    for c in xrange(7):
        assert sorted([(x,y) for x,y in forest.edges(child=c)]) == \
               sorted([(x,y) for x,y in edges_to_add if y == c])
        assert len([e for e in forest.edges(child=c)]) <= 1

def test_roots(forest):
    forest.add_edge(0,1)
    forest.add_vertex(2)
    forest.add_vertex('a')
    forest.add_edge('X','Y')
    assert sorted(r for r in forest.roots()) == sorted([0,2,'a','X'])
    forest.add_edge(1,2)
    assert sorted(r for r in forest.roots()) == sorted([0,'a','X'])
    forest.add_edge('a','X')
    assert sorted(r for r in forest.roots()) == sorted([0,'a'])
    forest.add_edge('a',0)
    assert sorted(r for r in forest.roots()) == ['a']

def test_cycles_not_allowed(forest):
    forest.add_edge(0,1)
    forest.add_edge(0,2)
    py.test.raises(exceptions.CycleCreatedError, 'forest.add_edge(1,2)')
    py.test.raises(exceptions.CycleCreatedError, 'forest.add_edge(2,1)')
    py.test.raises(exceptions.CycleCreatedError, 'forest.add_edge(0,1)')
    py.test.raises(exceptions.CycleCreatedError, 'forest.add_edge(1,0)')

def test_auto_reverse_edges(forest):
    forest.add_edge(0,1)
    x,y = forest.add_edge(2,1)
    assert (x,y) == (1,2)
    x,y = forest.add_edge(3,0)
    assert (x,y) == (0,3)

def test_reroot_star(forest):
    for v in xrange(10):
        forest.add_edge(v,10)
    for v in xrange(10):
        forest.reroot(v)
        assert [r for r in forest.roots()] == [v]
        assert [(x,y) for x,y in forest.edges(child=10)] == [(v,10)]
        assert [(x,y) for x,y in forest.edges(parent=v)] == [(v,10)]
        assert sorted((x,y) for x,y in forest.edges(parent=10)) == \
               sorted((10,x) for x in xrange(10) if x != v)
        for u in xrange(10):
            if u == v:
                continue
            assert [(x,y) for x,y in forest.edges(child=u)] == [(10,u)]
            assert [(x,y) for x,y in forest.edges(parent=u)] == [] 
        
    forest.reroot(10)
    assert [r for r in forest.roots()] == [10]
    assert sorted((x,y) for x,y in forest.edges(parent=10)) == \
           sorted((10,x) for x in xrange(10))
    for x in xrange(10):
        assert sorted((x,y) for x,y in forest.edges(child=x)) == [(10,x)]
        assert [e for e in forest.edges(parent=x)] == []

def test_reroot_line(forest):
    forest.add_edge(0,1)
    forest.add_edge(1,2)
    forest.add_edge(2,3)
    forest.add_edge(3,4)
    forest.add_edge(4,5)

    forest.reroot(3)
    assert list(forest.roots()) == [3]
    assert sorted((x,y) for x,y in forest.edges(parent=3)) == \
           sorted([(3,2),(3,4)])
    assert list(forest.edges(child=3)) == []
    assert list((x,y) for x,y in forest.edges(parent=4)) == [(4,5)]
    assert list((x,y) for x,y in forest.edges(child=4)) == [(3,4)]
    assert list((x,y) for x,y in forest.edges(parent=5)) == []
    assert list((x,y) for x,y in forest.edges(child=5)) == [(4,5)]
    assert list((x,y) for x,y in forest.edges(parent=2)) == [(2,1)]
    assert list((x,y) for x,y in forest.edges(child=2)) == [(3,2)]
    assert list((x,y) for x,y in forest.edges(parent=1)) == [(1,0)]
    assert list((x,y) for x,y in forest.edges(child=1)) == [(2,1)]
    assert list((x,y) for x,y in forest.edges(parent=0)) == []
    assert list((x,y) for x,y in forest.edges(child=0)) == [(1,0)]

    forest.reroot(5)
    forest.reroot(0)
    assert list(forest.roots()) == [0]
    assert list((x,y) for x,y in forest.edges(parent=0)) == [(0,1)]
    assert list((x,y) for x,y in forest.edges(child=0)) == []
    assert list((x,y) for x,y in forest.edges(parent=1)) == [(1,2)]
    assert list((x,y) for x,y in forest.edges(child=1)) == [(0,1)]
    assert list((x,y) for x,y in forest.edges(parent=2)) == [(2,3)]
    assert list((x,y) for x,y in forest.edges(child=2)) == [(1,2)]
    assert list((x,y) for x,y in forest.edges(parent=3)) == [(3,4)]
    assert list((x,y) for x,y in forest.edges(child=3)) == [(2,3)]
    assert list((x,y) for x,y in forest.edges(parent=4)) == [(4,5)]
    assert list((x,y) for x,y in forest.edges(child=4)) == [(3,4)]
    assert list((x,y) for x,y in forest.edges(parent=5)) == []
    assert list((x,y) for x,y in forest.edges(child=5)) == [(4,5)]

def test_split(forest):
    forest.add_edge(0,1)
    forest.add_edge(0,2)
    forest.add_edge(1,3)
    forest.add_edge(3,'a')
    forest.add_edge(3,'b')
    forest.add_edge(3,'c')
    forest.add_edge(2,4)
    forest.add_edge(2,5)
    assert sorted(forest.roots()) == [0]
    forest.split(1)
    assert sorted(forest.roots()) == [0,1]
    assert list(forest.edges(child=1)) == []
    forest.split(1)
    assert sorted(forest.roots()) == [0,1]
    assert list(forest.edges(child=1)) == []
    forest.split('a')
    assert sorted(forest.roots()) == sorted([0,1,'a'])
    forest.split('b')
    assert sorted(forest.roots()) == sorted([0,1,'a','b'])
    forest.split('c')
    assert sorted(forest.roots()) == sorted([0,1,'a','b','c'])
    forest.split(2)
    assert sorted(forest.roots()) == sorted([0,1,2,'a','b','c'])
    forest.split(3)
    assert sorted(forest.roots()) == sorted([0,1,2,3,'a','b','c'])
    forest.split(4)
    assert sorted(forest.roots()) == sorted([0,1,2,3,4,'a','b','c'])
    forest.split(5)
    assert sorted(forest.roots()) == sorted([0,1,2,3,4,5,'a','b','c'])

def test_path(forest):
    forest.add_edge(0,1)
    forest.add_edge(0,2)
    forest.add_edge(0,3)
    forest.add_edge(1,4)
    forest.add_edge(1,5)
    forest.add_edge(2,6)
    forest.add_edge(2,7)
    forest.add_edge(2,8)
    forest.add_vertex('singleton1')
    forest.add_vertex('singleton2')
    forest.add_edge('a','b')
    forest.add_edge('b','c')
    forest.add_edge('c','d')
    forest.add_edge('d','e')
    forest.add_edge('e','f')
    forest.add_edge('a','g')
    forest.add_edge('g','h')
    forest.add_edge('h','i')
    forest.add_edge('i','j')
    forest.add_edge('j','k')

    # First, test vertices that shouldn't have paths between them
    for i in xrange(9):
        for j in 'abcdefghi':
            py.test.raises(exceptions.NoPathExistsError, 
                           "list(forest.path(%s,'%s'))" % (i,j))
            py.test.raises(exceptions.NoPathExistsError, 
                           "list(forest.path('%s',%s))" % (j,i))
            for endpoint in ('singleton1','singleton2'):
                py.test.raises(exceptions.NoPathExistsError, 
                               "list(forest.path(%s,'%s'))" % (i,endpoint))
                py.test.raises(exceptions.NoPathExistsError,
                               "list(forest.path('%s',%s))" % (endpoint,i))
                py.test.raises(exceptions.NoPathExistsError, 
                               "list(forest.path('%s','%s'))" % (j,endpoint))
                py.test.raises(exceptions.NoPathExistsError,
                               "list(forest.path('%s','%s'))" % (endpoint,j))

    # Now, test vertices that should have paths between them
    assert [(x,y) for x,y in forest.path(5,4)] == [(5,1),(1,4)]
    assert [(x,y) for x,y in forest.path(4,5)] == [(4,1),(1,5)]
    assert [(x,y) for x,y in forest.path(5,8)] == [(5,1),(1,0),(0,2),(2,8)]
    assert [(x,y) for x,y in forest.path(8,5)] == [(8,2),(2,0),(0,1),(1,5)]
    assert [(x,y) for x,y in forest.path(8,2)] == [(8,2)]
    assert [(x,y) for x,y in forest.path(2,8)] == [(2,8)]

    full_path = [('a','b'), ('b','c'), ('c','d'), ('d','e'), ('e','f')]
    vertices = 'abcdef'
    for i,u in enumerate(vertices):
        for j,v in enumerate(vertices):
            if i >= j:
                continue
            assert [(x,y) for x,y in forest.path(u,v)] == full_path[i:j]
            assert [(x,y) for x,y in forest.path(v,u)] == \
                   [(y,x) for x,y in reversed(full_path[i:j])]

    vertices_other = 'aghijk'
    full_path_other = [('a','g'),('g','h'),('h','i'),('i','j'),('j','k')]
    for i,u in enumerate(vertices):
        for j,v in enumerate(vertices_other):
            first = full_path[0:i]
            second = [(y,x) for x,y in full_path_other[0:j]][::-1]
            assert [(x,y) for x,y in forest.path(v,u)] == second + first
            assert [(x,y) for x,y in forest.path(u,v)] == \
                   [(y,x) for x,y in first][::-1] + \
                   [(y,x) for x,y in second][::-1]

def test_source_target_compatibility(forest):
    forest.add_edge(0,1)
    forest.add_edge(1,2)
    forest.add_edge(2,3)
    forest.add_edge(0,4)
    forest.add_edge(4,5)
    forest.add_edge(4,6)
    forest.add_edge(6,7)
    forest.add_edge(0,8)
    forest.add_edge(8,9)
    for v in forest.vertices():
        assert sorted((x,y) for x,y in forest.edges(source=v)) == \
               sorted((x,y) for x,y in forest.edges(parent=v))
        assert sorted((x,y) for x,y in forest.edges(target=v)) == \
               sorted((x,y) for x,y in forest.edges(child=v))
        for u in forest.vertices():
            assert [(x,y) for x,y in forest.edges(source=u,target=v)] == \
                   [(x,y) for x,y in forest.edges(parent=u,child=v)]

def test_remove_vertex(forest):
    forest.add_edge('a','b')
    forest.add_edge('b','c')
    forest.add_edge('b','d')
    forest.add_edge('d','e')
    forest.add_edge('d','f')
    forest.remove_vertex('b')
    assert sorted(r for r in forest.roots()) == sorted(['a','c','d'])
    assert sorted(v for v in forest.vertices()) == \
           sorted(['a','c','d','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == \
           sorted([('d','e'), ('d','f')])
    forest.add_edge('a','b')
    assert sorted(r for r in forest.roots()) == sorted(['a','c','d'])
    assert sorted(v for v in forest.vertices()) == \
           sorted(['a','b','c','d','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == \
           sorted([('a','b'),('d','e'), ('d','f')])
    forest.remove_vertex('b')
    assert sorted(r for r in forest.roots()) == sorted(['a','c','d'])
    assert sorted(v for v in forest.vertices()) == \
           sorted(['a','c','d','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == \
           sorted([('d','e'), ('d','f')])
    forest.add_vertex('b')
    assert sorted(r for r in forest.roots()) == sorted(['a','b','c','d'])
    assert sorted(v for v in forest.vertices()) == \
           sorted(['a','b','c','d','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == \
           sorted([('d','e'), ('d','f')])
    forest.remove_vertex('b')
    assert sorted(r for r in forest.roots()) == sorted(['a','c','d'])
    assert sorted(v for v in forest.vertices()) == \
           sorted(['a','c','d','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == \
           sorted([('d','e'), ('d','f')])
    forest.remove_vertex('a')
    assert sorted(r for r in forest.roots()) == sorted(['c','d'])
    assert sorted(v for v in forest.vertices()) == \
           sorted(['c','d','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == \
           sorted([('d','e'), ('d','f')])
    forest.remove_vertex('d')
    assert sorted(r for r in forest.roots()) == ['c', 'e', 'f']
    assert sorted(v for v in forest.vertices()) == \
           sorted(['c','e','f'])
    assert sorted((x,y) for x,y in forest.edges()) == []
    forest.remove_vertex('e')
    assert sorted(r for r in forest.roots()) == ['c', 'f']
    assert sorted(v for v in forest.vertices()) == \
           sorted(['c','f'])
    assert sorted((x,y) for x,y in forest.edges()) == []
    forest.remove_vertex('c')
    assert sorted(r for r in forest.roots()) == ['f']
    assert sorted(v for v in forest.vertices()) == ['f']
    assert sorted((x,y) for x,y in forest.edges()) == []
    forest.remove_vertex('f')
    assert sorted(r for r in forest.roots()) == []
    assert sorted(v for v in forest.vertices()) == []
    assert sorted((x,y) for x,y in forest.edges()) == []

def test_remove_vertex_unknown(forest):
    py.test.raises(exceptions.VertexNotFoundError, 'forest.remove_vertex(0)')
    forest.add_vertex(0)
    forest.remove_vertex(0)
    py.test.raises(exceptions.VertexNotFoundError, 'forest.remove_vertex(0)')

def test_construct_with_vertex_list(forest_type):
    f1 = forest_type(vertices = xrange(10))
    f2 = forest_type()
    for i in xrange(10):
        f2.add_vertex(i)
    assert sorted(f1.vertices()) == sorted(f2.vertices())
    assert sorted((x,y) for x,y in f1.edges()) == \
           sorted((x,y) for x,y in f2.edges())

def test_construct_with_edge_list(forest_type):
    edge_list = [(0,1),(1,2),(2,3),(2,4),('a','b')]
    f1 = forest_type(edges = edge_list)
    f2 = forest_type()
    for e in edge_list:
        for v in e:
            f2.add_vertex(v)
    for u,v in edge_list:
        f2.add_edge(u,v)
    f3 = forest_type()
    for u,v in edge_list:
        f3.add_edge(f3.add_vertex(u), f3.add_vertex(v))
    assert sorted(f1.vertices()) == sorted(f2.vertices())
    assert sorted(f1.vertices()) == sorted(f3.vertices())
    assert sorted([(x,y) for x,y in f1.edges()]) == \
           sorted([(x,y) for x,y in f2.edges()])
    assert sorted([(x,y) for x,y in f1.edges()]) == \
           sorted([(x,y) for x,y in f3.edges()])

def test_property_get(forest):
    pass
