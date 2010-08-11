import yaupon
from yaupon.traversal import *

def test_revisit_state():
    g = yaupon.Graph(vertices = 'abcdef')
    g.add_property('edge_weight')
    g.add_property('vertex_cost')

    #             0

    g.vertex_cost['a'] = 8
    g.edge_weight[g.add_edge('a','b')] = 2
    g.vertex_cost['b'] = 7
    g.edge_weight[g.add_edge('a','c')] = 2
    g.vertex_cost['c'] = 3
    g.edge_weight[g.add_edge('b','d')] = 1
    g.edge_weight[g.add_edge('c','d')] = 2
    g.vertex_cost['d'] = 8
    g.edge_weight[g.add_edge('d','e')] = 2
    g.vertex_cost['e'] = 1
    g.edge_weight[g.add_edge('e','f')] = 8
    g.vertex_cost['f'] = 0
