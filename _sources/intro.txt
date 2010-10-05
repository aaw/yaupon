
Quick start
===========

To start, we'll build a simple graph with two vertices and one edge::

   >>> from yaupon import Graph
   >>> g = Graph()
   >>> nyc = g.add_vertex('New York, NY')
   >>> bos = g.add_vertex('Boston, MA')
   >>> e = g.add_edge(nyc, bos)

We can now iterate over all vertices or all edges::

   >>> for v in g.vertices():
   ...     print(v)
   ...
   New York, NY
   Boston, MA
   >>> for e in g.edges():
   ...     print(e)
   ...
   ('New York, NY', 'Boston, MA')
 
Let's add a few more vertices and edges::

   >>> chi = g.add_vertex('Chicago, IL')
   >>> lax = g.add_vertex('Los Angeles, CA')
   >>> f = g.add_edge(chi, nyc)
   >>> g = g.add_edge(chi, lax)

We can also iterate over edges by specifying the source, target, or
both::

   >>> for e in g.edges(source = chi):
   ...     print(e)
   ...
   ('Chicago, IL', 'New York, NY')
   ('Chicago, IL', 'Los Angeles, CA')
   >>> for e in g.edges(target = bos):
   ...     print(e)
   ...
   ('New York, NY', 'Boston, MA')



