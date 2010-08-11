yaupon's Graph Interface
========================

yaupon's graph interface makes a distinction between three main concepts:
vertices, edges, and properties.

yaupon's graph interface makes no explicit distinction between directed and 
undirected graphs. Each edge must specify a "source" and "target" vertex and 
graphs allow iteration over edges by specifying a source, a target, or both a 
source and target.

The vertices of a graph are a set of any hashable, comparable Python objects.

Adding vertices
~~~~~~~~~~~~~~~

Vertices can be added to a graph in one of two ways: either by passing a 
sequence of vertices at construction::

   >>> g = yaupon.Graph(vertices = ['a','b','c'])

or by calling the *add_vertex* method::

   >>> g.add_vertex('d')
   'd'

*add_vertex* can also be called without an argument, in which case the graph 
is responsible for generating some unique handle for the new vertex::

   >>> g.add_vertex()
   UUID('ee2d7e1f-a0a6-42e2-abaf-665a6a377f49')

In either case, *add_vertex* returns the vertex that was just added. If 
*add_vertex* is called on a vertex that already exists in the graph, the
existing vertex is returned::

   >>> g.add_vertex('X')
   'X'
   >>> g.add_vertex('X')
   'X'

Iterating over vertices
~~~~~~~~~~~~~~~~~~~~~~~

The *vertices* method returns an iterator over the vertices in a graph::

   >>> g = yaupon.Graph(vertices = ['a', 'b'])
   >>> g.add_vertex('c')
   'c'
   >>> [v for v in g.vertices()]
   ['a', 'b', 'c']

Adding edges
~~~~~~~~~~~~

Edges can be added to a graph in one of two ways: either by passing a sequence
of edges to the graph constructor::

    >>> g = yaupon.Graph(edges = [('BOS', 'LGA'), ('LGA', 'ORD')])

or by calling the *add_edge* method.::

    >>> g = yaupon.Graph()
    >>> g.add_edge('BOS', 'LGA')
    ('BOS', 'LGA')

In either case, pairs of vertices, not edges, are passed to the graph and the 
graph creates the actual edge objects. *add_edge* returns the edge object 
created. You can alter the type that the graph uses to construct the edge
by setting the *graph.EdgeType* parameter (TODO: this should just be a 
constructor parameter).
The vertices in the edge will be added to the vertex set if necessary, so 
the call::

    >>> g.add_edge(x,y)

has the same effect as::
 
    >>> g.add_edge(g.add_vertex(x), g.add_vertex(y))

Edges with the same source and target (loops) are allowed. Edges with the same
source and target as another edge in the graph (multi-edges) may be allowed
if the graph chooses to support multi-edges. All of 

Iterating over edges
~~~~~~~~~~~~~~~~~~~~

The *edges* method returns an iterator over edges in the graph::

    >>> g = yaupon.Graph(edges = [('a', 'b')])
    >>> g.add_edge('c', 'd')
    ('c', 'd')
    >>> [e for e in g.edges()]
    [('a', 'b'), ('c', 'd')]

*edges* also accepts two optional named arguments: *source* and *target*,
which allow you to iterate over edges by filtering on a particular source
or target::

    >>> g = yaupon.Graph(edges = [(0, 1), (2, 3), (2, 3), (0, 2), (4, 2)])
    >>> [e for e in g.edges(source = 0)]
    [(0, 1), (0, 2)]
    >>> [e for e in g.edges(target = 2)]
    [(0, 2), (4, 2)]
    >>> [e for e in g.edges(source = 2, target = 3)]
    [(2, 3), (2, 3)]
    >>> [e for e in g.edges(source = 'a')]
    []

Removing vertices
~~~~~~~~~~~~~~~~~

Removing edges
~~~~~~~~~~~~~~

Properties
~~~~~~~~~~

*Properties* are mappings from vertices or edges to Python objects. Storage
and management of properties is provided by the graph implementation::

    >>> import yaupon
    >>> g = yaupon.Graph(edges = [(0,1),(2,3)])
    >>> g.add_property('vertex_color')
    >>> g.vertex_color[0] = 'red'
    >>> g.vertex_color[1] = 'blue'
    >>> g.add_property('edge_weight')
    >>> e,f = g.edges()
    >>> g.edge_weight[e] = 1.4
    >>> g.edge_weight[f] = 2.22

Properties implement a subset of the Python dict interface - just the index
operator ([]) that allows getting and setting, and the "get" method.

Properties are considered part of the graph and are serialized along with
vertices and edges by ygp. *add_property* with a string argument causes 
a new property to be created and associated with the graph::

    >>> import yaupon
    >>> g = yaupon.Graph(edges = [('a','b'),('c','d')]
    >>> g.add_property('vertex_weight')

The property is then accessible as an object property::

    >>> g.vertex_weight['a'] = 2
    >>> g.vertex_weight['b'] = 3

You can access a dictionary that maps property names to properties by calling 
*properties*::

    >>> g.properties().keys()
    ['vertex_weight']

Finally, you can remove a property from a graph by calling *remove_property*::

    >>> g.remove_property('vertex_weight')
    >>> g.properties()
    {}

Nothing distinguishes vertex properties from edge properties. We recommend the 
convention of prefixing vertex properties with "vertex\_" and edge properties 
with "edge\_".