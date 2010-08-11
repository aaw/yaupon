import yaupon.io.ygp
from yaupon.tests.testutils import TempFile, pytest_generate_tests

def test_ygp_to_file(graph_type):
    g = graph_type()
    for u,v in [(1,2),(2,1),('a','a'),(22,'hello')]:
        g.add_edge(u,v)
    g.add_property('vertex_name')
    g.add_property('edge_weight')
    g.vertex_name[1] = 'one'
    g.vertex_name['a'] = 'A VERTEX'
    a = [e for e in g.edges(source = 1)][0]
    b = [e for e in g.edges(source = 22)][0]
    c = [e for e in g.edges(source = 'a')][0]
    d = [e for e in g.edges(source = 2)][0]
    g.edge_weight[a] = 12.2
    g.edge_weight[b] = 'hello world'

    tf = TempFile()
    f = tf.open('wb')
    yaupon.io.ygp.dump(f, g)
    tf.close()

    h = graph_type()
    yaupon.io.ygp.load(tf.open('rb'), h)

    assert sorted(v for v in g.vertices()) == sorted(v for v in h.vertices())
    assert sorted((u,v) for u,v in g.edges()) == \
           sorted((u,v) for u,v in h.edges())
    h_a = [e for e in h.edges(source = 1)][0]
    h_b = [e for e in h.edges(source = 22)][0]
    h_c = [e for e in h.edges(source = 'a')][0]
    h_d = [e for e in h.edges(source = 2)][0]
    for prop_name, prop in g.properties().items():
        h_prop = h.properties()[prop_name]
        assert prop.get(a) == h_prop.get(h_a)
        assert prop.get(b) == h_prop.get(h_b)
        assert prop.get(c) == h_prop.get(h_c)
        assert prop.get(d) == h_prop.get(h_d)

