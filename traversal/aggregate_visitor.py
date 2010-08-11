from visitor import TraversalVisitor
from yaupon.util.shortcuts import other_vertex
from yaupon.backend import BackendCore, getbackend
from yaupon.data_structures import ydict

class CompositeVisitor(TraversalVisitor):
    dependencies = []
    
    def __init__(self, agg):
        TraversalVisitor.__init__(self)
        self.properties = agg
        self.value = ydict(backend=agg)

class DiscoverTime(CompositeVisitor):
    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)
        self.next_timestamp = 0

    def discover_vertex(self, v):
        self.value[v] = self.next_timestamp
        self.next_timestamp += 1

class ParentEdge(CompositeVisitor):
    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)

    def discover_vertex(self, v):
        self.value[v] = None

    def tree_edge(self, e):
        u,v = e
        self.value[v] = e

class LowPoint(CompositeVisitor):
    dependencies = [DiscoverTime]

    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)

    def discover_vertex(self, v):
        self.value[v] = self.properties[DiscoverTime][v]

    def tree_edge(self, e):
        u,v = e
        self.value[u] = min(self.value[u], self.value[v])

    def back_edge(self, e):
        u,v = e
        v_discover_time = self.properties[DiscoverTime][v]
        self.value[u] = min(self.value[u], v_discover_time)

class LeastAncestor(CompositeVisitor):
    dependencies = [DiscoverTime]

    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)

    def discover_vertex(self, v):
        self.value[v] = self.properties[DiscoverTime][v]

    def tree_edge(self, e):
        u,v = e
        self.value[v] = self.properties[DiscoverTime][u]

    def back_edge(self, e):
        u,v = e
        self.value[u] = min(self.value[u], 
                            self.properties[DiscoverTime][v])
    
class Parent(CompositeVisitor):
    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)

    def discover_vertex(self, v):
        self.value[v] = None

    def tree_edge(self, e):
        u,v = e
        self.value[v] = u

class Depth(CompositeVisitor):
    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)

    def discover_vertex(self, v):
        self.value[v] = 0

    def tree_edge(self, e):
        parent, v = e
        self.value[v] = self.value.setdefault(parent,0) + 1



class AggregateVisitor(TraversalVisitor):
    def __init__(self, visitors, backend=None):
        TraversalVisitor.__init__(self)
        self.visitor_instances = {}
        self.visitors_by_name = {}
        self.visit_order = []
        if backend is None:
            backend = BackendCore()
        self.backend = backend
        for visitor_type in visitors:
            self.add_visitor(visitor_type)

    def add_visitor(self, visitor_type):
        if visitor_type not in self.visitor_instances:
            visitor_instance = visitor_type(self)
            self.visitor_instances[visitor_type] = visitor_instance
            self.visitors_by_name[visitor_type.__name__] = visitor_instance
            self.visit_order = []
            self.compute_dependencies(visitor_type)
            for v in self.visitor_instances:
                self.compute_dependencies(v)
    
    def compute_dependencies(self, visitor_type):
        for dependency in visitor_type.dependencies:
            if dependency not in self.visitor_instances:
                self.visitor_instances[dependency] = dependency(self)
            if dependency not in self.visit_order:
                self.compute_dependencies(dependency)
        if not [x for x in self.visit_order if type(x) == visitor_type]:
            self.visit_order.append(self.visitor_instances[visitor_type])

    def __getattr__(self, name):
        visitor = self.visitors_by_name.get(name)
        if visitor is None:
            raise AttributeError(name)
        return visitor.value

    def start_traversal(self, v):
        for visitor in self.visit_order:
            visitor.start_traversal(v)
    
    def discover_vertex(self, v):
        TraversalVisitor.discover_vertex(self,v)
        for visitor in self.visit_order:
            visitor.discover_vertex(v)
        
    def finish_vertex(self, v):
        for visitor in self.visit_order:
            visitor.finish_vertex(v)
        
    def tree_edge(self, e):
        for visitor in self.visit_order:
            visitor.tree_edge(e)
    
    def back_edge(self, e):
        for visitor in self.visit_order:
            visitor.back_edge(e)

    def forward_or_cross_edge(self, e):
        for visitor in self.visit_order:
            visitor.back_edge(e)


