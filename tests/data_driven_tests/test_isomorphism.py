import py.test

import yaupon
from yaupon.tests.testutils import graph_database_iteration
import yaupon.algorithm.isomorphism as isomorphism
import yaupon.algorithm.exceptions

def pytest_generate_tests(metafunc):
    graph_database_iteration(metafunc)

def test_isomorphism(graph):
    g = graph()
    g2 = yaupon.Graph()
    vertex_mapping = {}
    for v in reversed([x for x in g.vertices()]):
        vertex_mapping[v] = g2.add_vertex()
    for u,v in g.edges():
        g2.add_edge(vertex_mapping[u], vertex_mapping[v])
    #TODO: replicate properties, once they're taken into account by
    #      isomorphism algorithm
    iso = isomorphism.compile(g,g2)
    image_edges = set()
    for u,v in g.edges():
        g2_edges = [x for x in g2.edges(source=iso[u],
                                        target=iso[v])]
        for edge in g2_edges:
            assert edge not in image_edges
            image_edges.add(edge)
    assert len([e for e in g.edges()]) == len(image_edges)

def test_different_number_of_vertices(graph):
    g = graph()
    g2 = yaupon.Graph()
    vertex_mapping = {}
    for v in g.vertices():
        vertex_mapping[v] = g2.add_vertex()
    for u,v in g.edges():
        g2.add_edge(vertex_mapping[u], vertex_mapping[v])
    last_vertex = [x for x in g2.vertices()][-1]
    g2.remove_vertex(last_vertex)
    py.test.raises(yaupon.algorithm.exceptions.NoIsomorphismExists,
                   'isomorphism.compile(g,g2)')

def test_different_number_of_edges(graph):
    g = graph()
    g2 = yaupon.Graph()
    vertex_mapping = {}
    for v in g.vertices():
        vertex_mapping[v] = g2.add_vertex()
    for u,v in g.edges():
        g2.add_edge(vertex_mapping[u], vertex_mapping[v])
    last_edge = [x for x in g2.edges()][-1]
    g2.remove_edge(last_edge)
    py.test.raises(yaupon.algorithm.exceptions.NoIsomorphismExists,
                   'isomorphism.compile(g,g2)')

def test_not_an_isomorphism(graph):
    """
    Make four instances of each graph. Create an edge between
    the first two copies and call that g1 (which is connected.)
    Create an edge between two vertices in the third copy,
    then union that with the last copy to create g2 (which is
    not connected.) g1 and g2 have similar structure, and the
    same number of vertices and edges, but have different
    connected components so are not isomorphic
    """
    def union(g1,g2):
        v_map = {}
        for v in g2.vertices():
            v_map[v] = g1.add_vertex()
        for u,v in g2.edges():
            g1.add_edge(v_map[u], v_map[v])
        return g1

    g1_a = graph()
    g1_b = graph()
    g1_a_vertices = [v for v in g1_a.vertices()]

    g2_a = graph()
    g2_b = graph()
    g2_a_vertices = [v for v in g2_a.vertices()]

    g2_u, g2_v = g2_a_vertices[0], g2_a_vertices[-1]

    g1 = union(g1_a, g1_b)
    g2 = union(g2_a, g2_b)

    g1_u = g1_a_vertices[0]
    g1_v = [v for v in g1.vertices() if v not in g1_a_vertices][0]

    g1.add_edge(g1_u, g1_v)
    g2.add_edge(g2_u, g2_v)

    py.test.raises(yaupon.algorithm.exceptions.NoIsomorphismExists,
                   'isomorphism.compile(g1,g2)')

