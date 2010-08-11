import edge
import id_generators
from yaupon.graph_impl.exceptions import *
from yaupon.util.shortcuts import other_vertex, reverse_edge


class Forest(object):
    
    def __init__(self, vertices = None, edges = None):
        self.__parent_edge = {}
        self.__child_edges = {}
        self.EdgeType = edge.MultiEdge
        self.GenerateVertexName = id_generators.UUIDGenerator()
        if vertices is not None:
            for vertex in vertices:
                self.add_vertex(vertex)
        if edges is not None:
            for x,y in edges:
                self.add_edge(x,y)

    def vertices(self):
        return self.__parent_edge.iterkeys()

    def edges(self, parent=None, child=None, source=None, target=None):
        if source is not None:
            parent = source
        if target is not None:
            child = target
        if parent is None and child is None:
            for e in self.__parent_edge.itervalues():
                if e is not None:
                    yield e
        elif parent is not None and child is None:
            for e in self.__child_edges[parent]:
                yield e
        else:
            parent_edge = self.__parent_edge[child]
            if parent_edge is not None and \
               (parent is None or parent == parent_edge[0]):
                yield parent_edge

    def add_vertex(self, vertex=None):
        if vertex is None:
            vertex = self.GenerateVertexName()
        self.__parent_edge.setdefault(vertex, None)
        self.__child_edges.setdefault(vertex, [])
        return vertex

    def add_edge(self, parent, child):
        parent_exists = parent in self.__parent_edge
        child_exists = child in self.__parent_edge
        if parent_exists and child_exists:
            try:
                path = [e for e in self.path(child, parent)]
                raise CycleCreatedError(path)
            except NoPathExistsError:
                self.reroot(child)
        elif child_exists:
            parent,child = child,parent
        # Now, child's parent is None so we can attach it as a child to parent

        parent_children = self.__child_edges.get(parent)
        edge = self.EdgeType(parent, child)
        if parent_children is None:
            parent_children = self.__child_edges.get(self.add_vertex(parent))
        self.__parent_edge[child] = edge
        parent_children.append(edge)

        child_children = self.__child_edges.get(child)
        if not child_children:
            self.__child_edges[child] = []

        return edge

    def roots(self):
        for v,e in self.__parent_edge.items():
            if e is None:
                yield v

    def remove_vertex(self, v):
        if v not in self.__parent_edge:
            raise VertexNotFoundError(v)
        parent_edge = self.__parent_edge.pop(v)
        if parent_edge is not None:
            parent = other_vertex(parent_edge, v)
            self.__child_edges[parent].remove(parent_edge)
        for edge in self.__child_edges[v]:
            self.__parent_edge[other_vertex(edge, v)] = None
        del self.__child_edges[v]

    def path(self, source, target):
        if source == target:
            return
        starting_source, starting_target = source, target
        vertices_seen = set([source, target])
        s_iter = self.__parent_edge.get(source)
        t_iter = self.__parent_edge.get(target)
        s_path, t_path = [], []
        while s_iter != t_iter:
            if s_iter is not None:
                s_path.append(s_iter)
                source = other_vertex(s_iter, source)
                if source in vertices_seen:
                    break
                vertices_seen.add(source)
                s_iter = self.__parent_edge.get(source)

            if t_iter is not None:
                t_path.append(t_iter)
                target = other_vertex(t_iter, target)
                if target in vertices_seen:
                    break
                vertices_seen.add(target)
                t_iter = self.__parent_edge.get(target)

        if s_iter is None and t_iter is None:
            raise NoPathExistsError

        if source == starting_target or source == target:
            for edge in s_path:
                yield reverse_edge(edge)
        if target == starting_source or source == target:
            for edge in reversed(t_path):
                yield edge

    def reroot(self, v):
        current_node = v
        deferred_edges = list()
        
        while self.__parent_edge[current_node] is not None:
            parent_edge = self.__parent_edge[current_node]
            self.split(current_node)
            deferred_edges.append(reverse_edge(parent_edge))
            current_node = other_vertex(parent_edge, current_node)
        
        for edge in deferred_edges:
            self.add_edge(*edge)

    def split(self, v):
        """
        Given a vertex u, remove the edge from u to u's parent so
        they are in separate trees
        """
        edge = self.__parent_edge.get(v)
        if edge is None:
            return
        w = other_vertex(edge, v)
        self.__parent_edge[v] = None
        self.__child_edges[w].remove(edge)
