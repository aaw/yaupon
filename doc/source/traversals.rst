==========
Traversals
==========

A traversal is a systematic exploration of all vertices and edges in a graph. 
Traversals keep track of the vertices and edges have been explored previously 
and use this information to iteratively expand the 
:term:`traversal frontier`. Traversals differ by the
rules they use to choose a vertex or edge for exploration from among those on
the traversal frontier.

Building a traversal with yaupon involves calling yaupon's ``traverse``
function with the following three arguments:

 * An :ref:`initial_vertex_sequence`, used by the traversal to
   bootstrap its discovery of the graph. Whenever the traversal has completely
   explored the portion of the graph reachable from an initial vertex, it 
   pulls another vertex from this sequence and attempts to expand the traversal
   frontier from that vertex. 
 * A :ref:`traversal_generator`, which generates an sequence of vertices and 
   edges of the graph as they are encountered, annotated with information 
   about the state of a vertex or edge with respect to the traversal.
 * A :ref:`traversal_visitor`, which  collects information about the graph as 
   it's explored, for example, the discover time of each vertex, the depth of 
   each vertex in the traversal tree, or the parent edge of each vertex in the 
   traversal tree.

The ``traverse`` function feeds a generator with vertices from the sequence of 
initial vertices. The generator expands as much of the graph as it can from
each of these vertices in turn, and the traversal examines state information
returned from the generator and translates that information into calls on
the traversal visitor.


Examples
~~~~~~~~

To start off, let's run a depth-first search on a graph that simply prints
out all of the vertices reachable from a particular vertex in the order they're
discovered. First, we create a visitor, which we'll derive from the base
class ``TraversalVisitor``::

   >>> import yaupon
   >>> from yaupon.traversal import *
   >>> class Visitor(TraversalVisitor):
           def discover_vertex(self, vertex):
               print vertex,

``TraversalVisitor`` has all visitor event points defined as no-ops - here
we've overridden exactly one event point, ``discover_vertex``, which will be
called on each vertex in the graph as they're discovered. Next, we'll create 
graph that has two :term:`components <connected component>`: the 
:term:`path` ``(0,1), (1,2), (2,3)`` and the :term:`cycle` ``(4,5), (5,6), 
(6,4)``. Neither component is reachable from the other:: 

   >>> g = yaupon.Graph(edges = [(0,1),(1,2),(2,3),(4,5),(5,6),(6,4)])

Now we call ``traverse``, passing ``[0]`` as the sequence of initial
vertices, an instance of ``Visitor`` as our visitor, and a depth-first
traversal generator to see all of the vertices in the component containing
vertex ``0`` printed to the console::

   >>> traverse([0], Visitor(), depth_first_generator(g))
   0 1 2 3

Of course, we could just as easily print out all vertices in the other
component by starting with a different initial vertex sequence::

   >>> traverse([5], Visitor(), depth_first_generator(g))
   5 6 4

Or print all of the vertices in the graph by using ``g.vertices()`` as
the sequence of initial vertices::

   >>> traverse(g.vertices(), Visitor(), depth_first_generator(g))
   0 1 2 3 4 5 6

While you can always define your own traversal visitor as we did above, 
yaupon comes with a few predefined visitors that can be used to accomplish
common traversal tasks such as timestamping vertices in the order they were
discovered or storing the edge through which a vertex was discovered.
These visitors can be combined using the class ``AggregateVisitor`` to 
collect several traversal properties. In the example below, we use an
``AggregateVisitor`` to record the ``ParentEdge`` of each vertex (the edge
it was discovered through), the ``DiscoverTime`` of each vertex, and the
``Depth`` of each vertex (the length of the path from a root to the given
vertex in the forest defined by ``ParentEdge``.)::

   >>> import yaupon
   >>> from yaupon.traversal import *
   >>> g = yaupon.Graph(edges = [(0,1), (1,2), (2,3), (0,4)])
   >>> visitor = AggregateVisitor(g, visitors=[ParentEdge, DiscoverTime, Depth])
   >>> traverse(g.vertices(), visitor, depth_first_generator(g))
   >>> visitor.ParentEdge
   {0: None, 1: (0,1), 2: (1,2), 3: (2,3), 4: (0,4)}
   >>> visitor.DiscoverTime
   {0: 0, 1: 2, 2: 3, 3: 4, 4: 1}
   >>> visitor.Depth
   {0: 0, 1: 1, 2: 2, 3: 3, 4: 1}

.. _initial_vertex_sequence:

Initial vertex sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The initial vertex sequence lets you control which parts of the graph are
explored by specifying which vertices the traversal can be started from.
Supplying an iterator over all vertices in the graph guarantees that the 
entire graph is explored.
If the graph is :term:`strongly connected`, you only need to supply a 
single vertex as the initial vertex sequence.

.. _traversal_generator:

Traversal Generator
~~~~~~~~~~~~~~~~~~~

A traversal generator keeps track of the :term:`traversal frontier`
and uses this information to iteratively generate the 
next vertex to be explored by the traversal. yaupon comes with several 
generator implementations:

.. toctree::
  :maxdepth: 1

  traversals/depth_first_generator
  traversals/breadth_first_generator
  traversals/best_first_generator
  traversals/uniform_cost_generator
  traversals/a_star_generator

You can also write your own traversal generator. A traversal generator is 
any class that exposes the two methods 
``bootstrap(vertex)`` and ``events()``. ``bootstrap(vertex)`` adds a 
vertex to the traversal frontier and ``events()`` yields
vertex and edge events, iteratively expanding the frontier until
it's empty. 

The vertex and edge events returned by ``events()`` are just 
python ``dict`` s. To get a feel for what these look like, we can use a
``breadth_first_generator`` directly::
  
   >>> import yaupon
   >>> from yaupon.traversal import *
   >>> g = yaupon.Graph(edges = [(0,1),(1,2),(1,3),(2,4),(3,5)])
   >>> generator = breadth_first_generator(g)
   >>> generator.bootstrap(0)
   True
   >>> for event in generator.events():
   ...     print(event)
   ... 
   {'vertex': 0, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'UNDISCOVERED', 'edge': (0,1), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 1, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'UNDISCOVERED', 'edge': (1,2), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'target_state': 'UNDISCOVERED', 'edge': (1,3), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 2, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'UNDISCOVERED', 'edge': (2,4), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 3, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'UNDISCOVERED', 'edge': (3,5), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 4, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'vertex': 5, 'state': 'FINISHED', 'type': 'VERTEX'}

``bootstrap`` returns ``True`` if the vertex passed as an argument is one
that hasn't yet been seen by the traversal and ``False`` otherwise. In the
example above, we started with a vertex (``0``) that could reach all other
vertices in the graph. But we could have just as easily started anywhere
else in the graph as long as we bootstrap appropriately::

   >>> generator = breadth_first_generator(g)
   >>> generator.bootstrap(2)
   True
   >>> for event in generator.events():
   ...     print event
   ... 
   {'vertex': 2, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'UNDISCOVERED', 'edge': (2,4), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 4, 'state': 'FINISHED', 'type': 'VERTEX'}
   >>> generator.bootstrap(2)
   False
   >>> generator.bootstrap(4)
   False
   >>> generator.bootstrap(1)
   True
   >>> for event in generator.events():
   ...     print event
   ... 
   {'vertex': 1, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'FINISHED', 'edge': (1,2), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'target_state': 'UNDISCOVERED', 'edge': (1,3), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 3, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'UNDISCOVERED', 'edge': (3,5), 'type': 'EDGE', 'source_state': 'FINISHED'}
   {'vertex': 5, 'state': 'FINISHED', 'type': 'VERTEX'}
   >>> generator.bootstrap(0)
   True
   >>> for event in generator.events():
   ...     print event
   ... 
   {'vertex': 0, 'state': 'FINISHED', 'type': 'VERTEX'}
   {'target_state': 'FINISHED', 'edge': (0,1), 'type': 'EDGE', 'source_state': 'FINISHED'}
   >>> any(generator.bootstrap(v) for v in g.vertices())
   False

As you can see from the examples above, you can run a lightweight traversal
using just a generator if you know how to interpret the events returned. A
full traversal, including hooking in a :ref:`traversal_visitor`, is a more
robust solution if you want to switch out different generators in your
traversal or aggregate several visitor computations together.

.. _traversal_visitor:

Traversal Visitor
~~~~~~~~~~~~~~~~~

Visitors collect information from a traversal. Common visitors such as those
that record the discovery timestamp of vertices and edges, the depth of the
discovery, the parent vertices or edges in the :term:`traversal tree` and 
more are
defined by yaupon for use in yaupon's ``AggregateVisitor`` class. Unless you
have a particular need that isn't met by ``AggregateVisitor``, you shouldn't
need to define your own visitors (but see :ref:`defining_a_custom_visitor`
below if you need to.)

Pre-defined visitors that can be used with ``AggregateVisitor`` include:

  * ``DiscoverTime``: computes the unique, 0-indexed timestep at which each vertex was discovered

  * ``Depth``: computes the length of the unique path to the root of in the :term:`traversal tree`

  * ``Parent``: computes the parent vertex in the :term:`traversal tree` for each vertex, or ``None`` for the root of the traversal tree.

  * ``ParentEdge``: computes the parent edge in the :term:`traversal tree` for each vertex, or ``None`` for the root of the traversal tree.

  * ``LowPoint``: computes the low point of each vertex, a value important in the depth-first search-based computation of :term:`articulation points <articulation point>`. 

  * ``LeastAncestor``: computes, for any vertex v, the minimum ``DiscoverTime`` of a vertex u attached to v through a :term:`back edge` ``(u,v)`` or a :term:`tree edge` ``(u,v)``. If no such vertex u exists, ``LeastAncestor`` returns v's ``DiscoverTime``.

``AggregateVisitor`` is aware of and respects dependencies between visitors.
``LowPoint`` and ``LeastAncestor``, for example, both depend on the computation
that ``DiscoverTime`` knows how to perform, but ``AggregateVisitor`` computes
all three quantities in one pass over the graph by adding a ``DiscoverTime``
visitor to the computation if you haven't already specified one but have
added a ``LowPoint`` or ``LeastAncestor`` visitor to the ``AggregateVisitor``,
and scheduling the computation of ``DiscoverTime`` ahead of either of the
other visitors at each event point along the traversal.

.. _defining_a_custom_visitor:

Defining a custom visitor
-------------------------

You can define your own custom visitor, by implementing the visitor
interface. The complete visitor interface is defined by the 
``TraversalVisitor`` class::

    class TraversalVisitor(object):    
        def start_traversal(self, v):
            pass
    
        def discover_vertex(self, v):
            pass
    
        def finish_vertex(self, v):
            pass
    
        def tree_edge(self, e):
            pass
    
        def back_edge(self, e):
            pass
    
        def forward_or_cross_edge(self, e):
            pass

Some of the methods in ``TraversalVisitor`` aren't strictly necessary,
depending on what kind of traversal generator you use. ``back_edge``,
for example, is called on each :term:`back edge`, which means it isn't
needed with a :term:`breadth-first traversal` generator because
breadth first traversals don't have back edges by definition.

