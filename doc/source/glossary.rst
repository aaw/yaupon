Glossary
========

Terms here may differs slightly from ...

.. glossary::
   :sorted:

   acyclic
      A graph is acyclic if it contains no :ref:`cycle <cycle-def>`

   connected
      An undirected graph G is connected if, for any two vertices u,v in V(G), 
      there is a path from u to v. A directed graph G is connected if, for any 
      two vertices u,v in V(G), there is either a path from u to v or a path 
      from v to u. See :ref:`strongly connected <strongly-connected-def>` for 
      a stronger form of connectedness defined in directed graphs.

   connected component
      A maximally :term:`connected` :term:`vertex-induced subgraph`. A
      component consists of all vertices mutually reachable from each other
      through a series of 0 or more edges.

   cycle
      A cycle in a graph G is a sequence of edges (u_0, v_0), (u_1, v_1), ..., 
      (u_(n-1), v_(n-1)) such that u_0, u_1, ..., u_(n-1) are all distinct and 
      v_i = u_(i+1 mod n) for all i

   edge-induced subgraph
      An edge-induced subgraph...

   forest
      A forest is a set of :ref:`trees <tree-def>` that share no common
      vertices

   graph
      A graph G is a set of vertices V(G) and a set of edges E(G). E(G) is any
      subset of V(G) x V(G), the set of all ordered pairs of vertices.

   path
      A path in a graph G is a sequence of edges (u_0, v_0), (u_1, v_1), ..., 
      (u_(n-1), v_(n-1)) such that u_0, u_1, ..., u_(n-1) are all distinct and 
      v_i = u_(i+1) for all i in [0..n-2]

   strongly connected
      A directed graph is strongly connected if, for every pair of vertices u,v
      in V(G), there is a :ref:`path <path-def>` from u to v and a path from v 
      to u.

   strongly connected component
      A blah blah

   traversal
      aasdfsa

   traversal frontier
      At any point in a :term:`traversal`, any vertex in the 
      graph can be categorized into exactly one of three states:

       * unexplored, if the traversal isn't yet aware of the vertex
       * undiscovered, if the traversal has seen the vertex but no out edges 
         from the vertex have been explored yet
       * discovered, if some but not all out edges from the vertex have been
         explored
       * finished, if all out edges from the vertex have been explored
   
      The traversal frontier consists of all undiscovered vertices.

   tree
      A tree is an undirected graph G that can be characterized by several 
      equivalent definitions:

       * G is :term:`acyclic` and :term:`connected`
       * G is minimally :term:`connected` (removing any edge 
         separates G into more than one :term:`connected component`)
       * G is maximally :term:`acyclic` (adding any edge creates a 
         cycle)
       * Between any two vertices in G, there exists a unique path

   vertex-induced subgraph
      A vertex-induced subgraph is ...

   traversal tree
      The :term:`tree` defined by the discovery order of vertices and edges
      in a :term:`traversal`. TODO: expand

   articulation point
      TODO TODO

   back edge
      In a :term:`depth-first traversal`, a back edge is ...

   tree edge
      In a :term:`traversal`, a tree edge is ...

   depth-first traversal
      A type of :term:`traversal` that ...

   breadth-first traversal
      A type of :term:`traversal` that ...