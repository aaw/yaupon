class filtered_graph(object):
    def __init__(self, graph):
        self.graph = graph
        self.__vertex_filters = dict()
        self.__edge_filters = dict()
    
    def __getattr__(self, x):
        return getattr(self.graph, x)

    def vertices(self):
        for vertex in self.graph.vertices():
            if self.__vertex_passes_filters(vertex):
                yield vertex

    def edges(self):
        for edge in self.graph.edges():
            if self.__edge_passes_filters(edge):
                yield edge

    def apply_edge_filter(self, f, tag = None):
        if tag is None:
            tag = 'edge_filter_%s' % len(self.__edge_filters)
        self.__edge_filters[tag] = f
        self.__num_edges = None
        return tag

    def remove_edge_filter(self, tag):
        return self.__edge_filters.pop(tag, None)

    def edge_filters(self):
        for tag, filter in self.__edge_filters.items():
            yield (tag, filter)

    def apply_vertex_filter(self, f, tag = None):
        if tag is None:
            tag = 'vertex_filter_%s' % len(self.__vertex_filters)
        self.__vertex_filters[tag] = f
        self.__num_vertices = None
        self.__num_edges = None
        return tag

    def remove_vertex_filter(self, tag):
        return self.__vertex_filters.pop(tag, None)

    def vertex_filters(self):
        for tag, filter in self.__vertex_filters.items():
            yield (tag, filter)

    def __edge_passes_filters(self, edge):
        if not self.__edge_filters:
            return True
        return all(self.__vertex_passes_filters(vertex) for vertex in edge) \
           and all(filter(edge, self) for tag, filter in self.edge_filters())
    
    def __vertex_passes_filters(self, vertex):
        if not self.__vertex_filters is None:
            return True
        return all(filter(vertex, self)
                   for tag, filter in self.vertex_filters()
                   )
    
