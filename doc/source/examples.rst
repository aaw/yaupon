
Examples
========

Sorting vertices by dependency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Drawing a graph
~~~~~~~~~~~~~~~

Solving a tile puzzle
~~~~~~~~~~~~~~~~~~~~~

A simple diff implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The output of a diff_ between two files is the shortest sequence of 
additions and deletions of lines of one file that would transform it
into the other. For example, given the file::

  yaupon is a graph library
  written in python
  designed to be easy to learn

and the file::

  yaupon is a graph library
  written entirely in python
  designed to be easy to learn
  and fun to use

a diff between the first and second file would tell you to replace the
line "written in python" with "written entirely in python" and to append
the line "and fun to use" to the end of the file.

In this section, we'll describe an algorithm for creating a diff
between two strings of text; the implementation is straightforward
to generalize to the more familiar diff implementation that operates
at the level of comparing entire lines in two files. 

Let's set up the description of the algorithm with an example: 
diffing the strings *bananas* and *cabana*. We'll start by drawing out
a two-dimensional grid, labelling the top horizontal axis with 
bananas and the left vertical axis with cabana::

        b   a   n   a   n   a   s
    +---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |
  c +---+---+---+---+---+---+---+
    |   | \ |   |   |   |   |   |
  a +---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |
  b +---+---+---+---+---+---+---+
    |   |   |   | \ |   |   |   |
  a +---+---+---+---+---+---+---+
    |   |   |   |   | \ |   |   |
  n +---+---+---+---+---+---+---+
    |   |   |   |   |   | \ |   |
  a +---+---+---+---+---+---+---+

A path in the above diagram from the upper left corner to the bottom
right corner defines a transformation from one string to the other: if
we assume that we're transforming bananas into cabana, we can read any
path from upper left corner to the bottom right corner and interpret
each horizontal edge as the operation "add the sx


.. _diff: http://en.wikipedia.org/wiki/Diff