Shortest Paths
==============

Shortest path algorithms attempt to find a path between two vertices (a source
and a target) in a graph that minimizes sum of the edge weights of the path. 
As long as the graph doesn't have a cycle with a negative weight sum between
the source and target vertex, this problem can be solved efficiently.

Without an edge weight function specified, the shortest path only takes the
number of edges between source and target into account::

    >>> import yaupon
    >>> import yaupon.algorithm.shortest_path as shortest_path
    >>> g = yaupon.Graph(edges = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,4)])
    >>> path = shortest_path.compile(graph=g, source=0)
    >>> [edge for edge in path(target=4)]
    [(0,5), (5,6), (6,4)]
    
If an edge weight function is specified, it must be specified at suite compile
time::

    >>> g.make_property('edge_weight')
    >>> for e in g.edges():
    ...     g.edge_weight[e] = 1
    >>> for e in g.edges(source=5, target=6):
    ...     g.edge_weight[e] = 100
    >>> path = shortest_path.compile(graph=g, 
    ...                              edge_weight=g.edge_weight, 
    ...                              source=0)
    >>> [edge for edge in path(target=4)]
    [(0,1), (1,2), (2,3), (3,4)]

But either source or target can be specified at either suite compile or call 
time::
 
    >>> path = shortest_path.compile(graph=g, edge_weight=g.edge_weight)
    >>> [edge for edge in path(source=0, target=3)]
    [(0,1), (1,2), (2,3)]
    >>> [edge for edge in path(source=3, target=6)]
    []
    >>> [edge for edge in path(source=5, target=6)]
    [(5,6)]

Negative edges are fine, as long as they don't cause a negative cycle in 
between the source and the target::

    >>> g.edge_weight[g.add_edge(5,'a')] = 10
    >>> g.edge_weight[g.add_edge('a','b')] = -19
    >>> g.edge_weight[g.add_edge('b',5)] = 10
    >>> path = shortest_path.compile(graph=g, edge_weight=g.edge_weight)
    >>> [edge for edge in path(source=0, target=4)]
    [(0,1), (1,2), (2,3), (3,4)]

If a negative cycle is between the source any target, a NegativeCycleError is
raised::

    >>> for edge in g.edges(source='a', target='b'):
    ...     g.edge_weight[edge] = -21
    >>> path = shortest_path.compile(graph=g, 
                                     edge_weight=g.edge_weight,
                                     source=0)
    Traceback (most recent call last):
    ...
    yaupon.algorithm.exceptions.NegativeCycleError

Some attempt is made to raise this exception as late as possible; in the above
example, if the suite had been compiled without a source or target specified,
the exception wouldn't have been thrown.

Algorithms used in this suite
-----------------------------

    * Dijkstra's shortest path algorithm
    * Bellman-Ford shortest path algorithm
    * Breadth-first search