import id_generators
import edge
import exceptions

# this is a bidirectional adjacency list: any edge (u,v)
# is on both self.__out_edges[u] and self.__in_edges[v]
class DictGraph(object):
    def __init__(self, vertices = None, edges = None):
        self.__out_edges = {}
        self.__in_edges = {}
        self.__properties = {}
        self.EdgeType = edge.MultiEdge
        self.GenerateVertexName = id_generators.UUIDGenerator()
        if vertices is not None:
            for v in vertices:
                self.add_vertex(v)
        if edges is not None:
            for x,y in edges:
                self.add_edge(self.add_vertex(x), self.add_vertex(y))

    def __getattr__(self, name):
        prop = self.__properties.get(name)
        if prop is None:
            raise AttributeError
        return prop

    def vertices(self):
        return self.__out_edges.iterkeys()

    def edges(self, source = None, target = None):
        if source is None and target is None:
            for adjacency_list in self.__out_edges.itervalues():
                for edge in adjacency_list:
                    yield edge
        elif target is None:
            for e in self.__out_edges[source]:
                yield e
        elif source is None:
            for e in self.__in_edges[target]:
                yield e
        else:
            for e in self.__out_edges[source]:
                if e[1] == target:
                    yield e

    def add_edge(self, source, target):
        edge = self.EdgeType(source, target)
        out_list = self.__out_edges.get(edge[0])
        in_list = self.__in_edges.get(edge[1])
        if out_list is None:
            out_list = self.__out_edges.get(self.add_vertex(edge[0]))
        if in_list is None:
            in_list = self.__in_edges.get(self.add_vertex(edge[1]))
        out_list.append(edge)
        in_list.append(edge)
        return edge

    def add_vertex(self, v = None):
        if v is None:
            v = self.GenerateVertexName()
        self.__out_edges.setdefault(v, [])
        self.__in_edges.setdefault(v, [])
        return v

    def remove_edge(self, edge):
        s, t = edge
        self.__out_edges[s] = [f for f in self.__out_edges[s] if f != edge]
        self.__in_edges[t] = [f for f in self.__in_edges[t] if f != edge]

    def remove_vertex(self, vertex):
        if vertex not in self.__out_edges:
            raise exceptions.VertexNotFoundError(vertex)
        for e in self.__out_edges[vertex]:
            t = e[1]
            self.__in_edges[t] = [f for f in self.__in_edges[t] if f != e]
        for e in self.__in_edges[vertex]:
            s = e[0]
            self.__out_edges[s] = [f for f in self.__out_edges[s] if f != e]
        self.__out_edges.pop(vertex)
        self.__in_edges.pop(vertex)

    def add_property(self, name):
        self.__properties[name] = {}
    
    def remove_property(self, name):
        del self.__properties[name]

    def properties(self):
        return self.__properties
