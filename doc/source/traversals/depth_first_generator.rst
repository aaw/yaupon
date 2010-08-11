===============================
Depth-first traversal generator
===============================

A depth-first traversal generator generates events for a 
:term:`depth-first traversal`, which always extends a path as far as
possible before backtracking.

Events generated
----------------

Example
-------

.. code-block:: python

    >>> import yaupon
    >>> from yaupon.traversal import *
    >>> g = yaupon.Graph(edges = [(0,1),(1,2),(2,3),(0,4),(4,5),(5,3),(0,6),(6,7)])
    >>> generator = depth_first_generator(g)
    >>> generator.bootstrap(0)
    True
    >>> for event in generator.events():
    ...     print(event)
    ... 
    {'target_state': 'UNDISCOVERED', 'edge': (0,6), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'target_state': 'UNDISCOVERED', 'edge': (6,7), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'vertex': 7, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'vertex': 6, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'target_state': 'UNDISCOVERED', 'edge': (0,4), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'target_state': 'UNDISCOVERED', 'edge': (4,5), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'target_state': 'UNDISCOVERED', 'edge': (5,3), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'vertex': 3, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'vertex': 5, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'vertex': 4, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'target_state': 'UNDISCOVERED', 'edge': (0,1), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'target_state': 'UNDISCOVERED', 'edge': (1,2), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'target_state': 'FINISHED', 'edge': (2,3), 'type': 'EDGE', 'source_state': 'DISCOVERED'}
    {'vertex': 2, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'vertex': 1, 'state': 'FINISHED', 'type': 'VERTEX'}
    {'vertex': 0, 'state': 'FINISHED', 'type': 'VERTEX'}
