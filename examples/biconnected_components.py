from graph import Graph
from graph.algorithm.traversal import traverse
from graph.algorithm.traversal.visitor import lowpoint_visitor


if __name__ = '__main__':
    g = Graph()
    g.add_edge(0,1)
    g.add_edge(1,2)
    g.add_edge(1,3)
    g.add_edge(2,4)
    g.add_edge(3,5)
    g.add_edge(1,5)

    low_point = lowpoint_visitor()
    traverse(lowpoint)
