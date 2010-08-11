from collections import defaultdict

import yaupon
from yaupon.tests.testutils import graph_database_iteration
from yaupon.traversal import *
from yaupon.adapters.undirected_graph import UndirectedGraph

def pytest_generate_tests(metafunc):
    graph_database_iteration(metafunc)

#def test_uniform_cost_search_vs_breadth_first_search(graph):
#    """
#    A uniform cost search tree should be isomorphic to the breadth-first
#    search tree if the uniform cost search was run with uniform edge weights.
#    TODO: implement forest_isomorpism
#    """
#    g = graph()
 

def test_uniform_search_produces_forest(graph):
    """
    If we hook up to the tree_edge event point of a visitor, the edges it
    produces should give us a forest.
    """
    g = graph()
    
    if hasattr(g, 'edge_weight'):
        edge_weight = g.edge_weight
    else:
        edge_weight = defaultdict(int)

    # Create a visitor that will produce a forest
    class ForestVisitor(TraversalVisitor):
        def __init__(self):
            TraversalVisitor.__init__(self)
            self.forest = yaupon.Forest()
        
        def tree_edge(self, e):
            # This will throw from inside "traverse" if a cycle is created
            self.forest.add_edge(e[0],e[1])

    forest_visitor = ForestVisitor()
    traverse(g.vertices(), forest_visitor, 
             uniform_cost_generator(g, edge_weight))
