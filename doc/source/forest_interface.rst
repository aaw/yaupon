yaupon's Forest Interface
=========================

A tree is a subclass of undirected graphs that can be used to model many different heirarchical 
relationships. A forest is a collection of trees.

yaupon's forest interface aims to match its graph interface in ways that would allow algorithms
to be easily reused and provide a few additional methods that have meaning only for forests.

Edges in a forest are always considered undirected, which means that the order of vertices within
an edge (when adding an edge or when iterating over existing edges) is arbitrary. Trees within a
forest can be "re-rooted", though, which can change the order in which vertices within an edge are
presented: when iterating over edges, vertices are always presented as a parent followed by a child.

Adding vertices
~~~~~~~~~~~~~~~

Vertices can be added to a forest in one of two ways: either by passing a 
sequence of vertices at construction::

   >>> f = yaupon.Forest(vertices = ['a','b','c'])

or by calling the *add_vertex* method::

   >>> f.add_vertex('d')
   d

``add_vertex`` can also be called without an argument, in which case the forest 
is responsible for generating some unique handle for the new vertex::

   >>> f.add_vertex()
   UUID('eeebea01-73b1-4ad9-8444-92edf5fcaeb5')

In either case, ``add_vertex`` returns the vertex that was just added. If 
``add_vertex`` is called on a vertex that already exists in the forest, the
existing vertex is returned::

   >>> f.add_vertex('X')
   'X'
   >>> f.add_vertex('X')
   'X'

Iterating over vertices
~~~~~~~~~~~~~~~~~~~~~~~

The *vertices* method returns an iterator over the vertices in a forest::

   >>> f = yaupon.Forest(vertices = ['a', 'b'])
   >>> f.add_vertex('c')
   'c'
   >>> [v for v in f.vertices()]
   ['a', 'b', 'c']

Adding edges
~~~~~~~~~~~~

Edges can be added to the graph either by using the ``add_edge`` method, or by
passing a list of vertex pairs to the forest constructor.
The ``add_edge`` method takes two vertices in the forest as arguments, creates
an edge in the forest between those two vertices as long as that edge does not
cause a cycle, and returns the new edge. Since edges in a forest are considered
undirected, the order in which you specify the two vertices in an edge doesn't matter,
and you may see edges "reversed"...

   >>> f = yaupon.Forest(vertices = xrange(1,10), edges = [(1,2),(2,3),(2,4)])
   >>> f.add_edge(4,5)
   (4,5)
   >>> f.add_edge(6,5)
   (5,6)

If a vertex is passed to ``add_edge`` that doesn't exist in the forest, it's added::

   >>> [v for v in g.vertices()]
   [1,2,3,4,5,6,7,8,9]
   >>> g.add_edge('a','b')
   (a,b)
   >>> [v for v in g.vertices()]
   ['a','b',1,2,3,4,5,6,7,8,9]

Since edges are undirected, two edges between the same two vertices are not allowed,
since they would create a cycle. If an edge is added that creates a cycle, a 
``CycleCreatedError`` is immediately raised.

   >>> f = yaupon.Forest(edges = [(1,2),(2,3)])
   >>> f.add_edge(1,3)
   Traceback (most recent call last):
   ...
       raise CycleCreatedError(path)
   yaupon.graph_impl.exceptions.CycleCreatedError: [(3,2), (2,1)]

The ``CycleCreatedError`` contains the path which would create a cycle with the edge
you're attempting to add.

Iterating over edges
~~~~~~~~~~~~~~~~~~~~

The ``edges`` method is used to iterate over edges in the graph. ``edges`` can be called
with no arguments, in which case all edges in the forest are returned::

   >>> f = yaupon.Forest(edges = [(1,2), (2,3), (3,4), ('a','b'))
   >>> [e for e in f.edges()]
   [(1,2), (2,3), (3,4), (a,b)]

Either or both of the named parameters ``parent`` and ``child`` may be used to iterate
over edges coming from a parent or going to a child, respectively::

   >>> f = yaupon.Forest(edges = [(0,1), (1,2), (1,3), (1,4)])
   >>> [e for e in f.edges(parent=1)]
   [(1,2), (1,3), (1,4)]
   >>> [e for e in f.edges(parent=4)]
   []
   >>> [e for e in f.edges(child=2)]
   [(1,2)]
   >>> [e for e in f.edges(child=0)]
   []
   >>> [e for e in f.edges(parent=1, child=4)]
   [(1,4)]
   >>> [e for e in f.edges(parent=4, child=1)]
   []

The named parameter ``source`` can be used interchangably with ``parent`` and the named
parameter ``target`` can be used interchangably with ``child``, for compatibility with
graph algorithms that use the same named parameters to iterate over edges. By rerooting
a graph, you can change the parent-child (or equivalently, source-target) relationship
between edges in a tree.

Iterating over roots
~~~~~~~~~~~~~~~~~~~~

Every tree in the forest has a single distinguished vertex called the root. The root
is the only vertex in the tree that is not the child of any other vertex in the tree.
Trees are often visualized as growing down from the root. 

The root of each tree depends on the order in which edges and vertices were inserted
into the forest and whether the tree has been explicitly rerooted (see :ref:`rerooting-a-tree`)::

   >>> f = yaupon.Forest(vertices = [0,1,2], edges = [('a','b'), ('b','c'), ('b','d')])
   >>> [r for r in f.roots()]
   [0, 1, 2, a]

.. _rerooting-a-tree:

Re-rooting a tree
~~~~~~~~~~~~~~~~~

If you re-root a tree around a vertex v, v is "rotated up", one edge at a time, until 
it becomes the root of the tree. One or more parent-child relationships within the 
tree may be reversed in the process::

   >>> f = yaupon.Forest(edges = [(1,2), (2,3), (2,4), (4,5), (4,6)])
   >>> [e for e in f.edges(child=4)]
   [(2,4)]
   >>> [e for e in f.edges(parent=4)]
   [(4,5), (4,6)]
   >>> [r for r in f.roots()]
   [1]
   >>> f.reroot(4)
   >>> [e for e in f.edges(child=4)]
   []
   >>> [e for e in f.edges(parent=4)]
   [(4,5), (4,6), (4,2)]
   >>> [r for r in f.roots()]
   [4]


Iterating over a path
~~~~~~~~~~~~~~~~~~~~~

Since it contains no cycles, a forest has at most one path between any two of its vertices:
if the vertices are in the same tree, there is a unique path between them. If they are in
different trees, there isn't a path between them. The ``path`` method can be used to find
the path between two vertices, if it exists::

   >>> f = yaupon.Forest(edges = [(0,1), (1,2), (1,3), (3,4), ('a','b'), ('a','c')])
   >>> [e for e in f.path(source=0, target=4)]
   [(0,1), (1,3), (3,4)]
   >>> [e for e in f.path(source=4, target=0)]
   [(4,3), (3,1), (1,0)]
   >>> [e for e in f.path(source='a', target='b')]
   [(a,b)]
   >>> [e for e in f.path(source='a', target='a')]
   []
   >>> [e for e in f.path(source=0, target='a')]
   Traceback (most recent call last):
   ...
   yaupon.graph_impl.exceptions.NoPathExistsError

Notice that a NoPathExistsError is raised if the two vertices supplied are in different 
trees, and an empty list is returned if the vertices are connected by the empty path
(which happens if source is equal to target.)

Removing an edge
~~~~~~~~~~~~~~~~

Edges can be removed from the forest through the ``split`` method, which takes a single
vertex and removes the parent edge, if any, connected to that vertex::

   >>> f = yaupon.Forest(edges = [(0,1), (1,2), (1,3)])
   >>> [r for r in f.roots()]
   [0]
   >>> f.split(1)
   >>> [r for r in f.roots()]
   [0, 1]
   >>> [e for e in f.edges()]
   [(1,2), (1,3)]
   
Removing a vertex
~~~~~~~~~~~~~~~~~

Removing a vertex from a forest also removes all edges incident upon that vertex,
which can split a tree into several trees::

   >>> f = yaupon.Forest(edges = [(0,1), (1,2), (1,3), (1,4)])
   >>> [r for r in f.roots()]
   [0]
   >>> f.remove_vertex(1)
   >>> [r for r in f.roots()]
   [0, 2, 3, 4]

A VertexNotFoundError is raised if you pass a vertex that doesn't exist in the forest::

   >>> f = yaupon.Forest()
   >>> f.remove_vertex(0)
   Traceback (most recent call last):
   ...
   yaupon.graph_impl.exceptions.VertexNotFoundError: 1






