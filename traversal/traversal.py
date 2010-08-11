from yaupon.util.shortcuts import other_vertex
from yaupon.traversal.traversal_exception import *


def traverse(root_vertices, visitor, generator):
    for vertex in root_vertices:
        traverse_from_vertex_helper(vertex, visitor, generator)


def traverse_from_vertex_helper(vertex, visitor, generator):

    if not generator.bootstrap(vertex):
        return

    visitor.start_traversal(vertex)
    visitor.discover_vertex(vertex)

    for record in generator.events():

        if record['type'] == 'VERTEX':
            #only state here is FINISHED
            visitor.finish_vertex(vertex)
        else:
            target_state, edge = record['target_state'], record['edge']
            if target_state == 'UNDISCOVERED':
                visitor.discover_vertex(edge[1])
                visitor.tree_edge(edge)
            elif target_state == 'DISCOVERED':
                visitor.back_edge(edge)
            elif target_state == 'FINISHED':
                visitor.forward_or_cross_edge(edge)
