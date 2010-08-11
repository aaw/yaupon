Backends
--------

Consider the following simple implementation of a traversal that prints 
all of the vertices in a graph breadth-first::

    first_vertex = graph.vertices().next()
    vertex_state = { first_vertex : 'VISITED' }
    vertices_to_visit = collections.deque([first_vertex])
    while vertices_to_visit:
        v = vertices_to_visit.popleft()
        state = vertex_state.get(v)
        if state is None:
            print 'Visiting %s' % v
            vertex_state[v] = 'VISITED'
            for v,w in graph.edges(source=v):
	        vertices_to_visit.append(w)

The problem with the code above is that it relies on a dictionary 
(``vertex_state``) and a deque (``vertices_to_visit``) that can both grow to
a size that's on the order of the size of the underlying graph. For graphs
that are stored in external memory, this means that the traversal might
exhaust available main memory even though the graph isn't being pulled into
main memory.

Ideally, we'd like to be able to write algorithms in a way that's completely
independent of how the graph is stored, so that our algorithms could be
used on in-memory graphs as well as graphs built on top of relational
databases, flat files, and other external storage. yaupon solves this problem 
by providing a protocol for a graph to pass information to an algorithm about 
how it should construct primitive data structures like a dict or a deque or 
how it should sort a sequence of values.

The backend protocol
~~~~~~~~~~~~~~~~~~~~

If a graph class wishes to take part in the backend protocol by specifying
how algorithms create fundamental data structures, it implements a method
named ``__backend__`` which takes no arguments and returns a yaupon backend. 
A yaupon backend is any class that implements three methods: 
``create_deque``, ``create_dict``, and ``sorted``. In addition, a yaupon
backend should also take part in the backend protocol by defining a
``__backend__`` method.

As an example, here's the definition of yaupon's ``BackendCore`` class, 
which is the default backend::

    class BackendCore(object):
        def __backend__(self):
            return self

        def create_deque(self, *args, **kwargs):
            return collections.deque(*args, **kwargs)

        def create_dict(self, *args, **kwargs):
            return dict(*args, **kwargs)

        def sorted(self, *args, **kwargs):
            return iter(sorted(*args, **kwargs))

To link all of this together, yaupon defines a function called ``getbackend``
that, when called with a class, returns either whatever the class returns from
its ``__backend__`` method or ``BackendCore`` if the class has no backend
method. This means that for any python object ``obj``, you can write::

    yaupon.getbackend(obj).create_dict()

to create a dict using whatever policy for creating dict-like objects the
object ``obj`` implements. As a convenience, yaupon also aliases these
calls as ``ydict``, ``ydeque``, and ``ysorted``, so that you write code
like::

    from yaupon import ydict, ydeque, ysorted, Graph
    g = Graph(edges=[(0,1),(1,2)])
    d = ydict(g, {1:2})
    for x in ysorted(g, g.vertices()):
        print x

Where the first argument of ``ydict``, ``ydeque``, and ``ysorted`` is anything
that might implement the yaupon backend protocol, and the remaining arguments
are anything you would pass to the constructor of Python's ``dict``, 
``collections.deque``, and ``sorted``, respectively.

Going back to our original example, we can now rewrite our traversal code
as::

    first_vertex = graph.vertices().next()
    vertex_state = ydict(graph, { first_vertex : 'VISITED' })
    vertices_to_visit = ydeque(graph, [first_vertex])
    while vertices_to_visit:
        v = vertices_to_visit.popleft()
        state = vertex_state.get(v)
        if state is None:
            print 'Visiting %s' % v
            vertex_state[v] = 'VISITED'
            for v,w in graph.edges(source=v):
	        vertices_to_visit.append(w)

and in doing so, respect whatever policy on memory for data structures that
``graph`` would like to enforce.

Beyond dicts, deques, and sorting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most other yaupon data structures...

A word of caution
~~~~~~~~~~~~~~~~~

Warn about nesting mutable classes within backends. For example, if you have
a SQLiteDict d and an instance c of some class C, set d[1] = c, and c.addone()
mutates c somehow, then d[1].addone() won't have the desired effect since
it's operating on an unpickled copy of c. class BackendCore(object):