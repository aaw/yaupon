from graph import Graph
from graph.algorithm import traverse



if __name__ = '__main__':
    g = Graph()
    g.add_edge(0,1)
    g.add_edge(1,2)
    g.add_edge(1,3)
    g.add_edge(2,4)
    g.add_edge(3,5)
    g.add_edge(1,5)

    print 'A topological sort is:'
    visitor = vertex_generator_visitor(depth_first_strategy())
    for vertex in traverse(visitor):
        print vertex
