from visitor import TraversalVisitor
from yaupon.util.shortcuts import other_vertex
from yaupon.backend import BackendCore, getbackend
from yaupon.data_structures import ydict
from yaupon.traversal.traversal_exception import SuccessfulTraversal

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
        self.value[v] = self.properties.DiscoverTime[v]

    def tree_edge(self, e):
        u,v = e
        self.value[u] = min(self.value[u], self.value[v])

    def back_edge(self, e):
        u,v = e
        v_discover_time = self.properties.DiscoverTime[v]
        self.value[u] = min(self.value[u], v_discover_time)

class LeastAncestor(CompositeVisitor):
    dependencies = [DiscoverTime]

    def __init__(self, agg):
        CompositeVisitor.__init__(self, agg)

    def discover_vertex(self, v):
        self.value[v] = self.properties.DiscoverTime[v]

    def tree_edge(self, e):
        u,v = e
        self.value[v] = self.properties.DiscoverTime[u]

    def back_edge(self, e):
        u,v = e
        self.value[u] = min(self.value[u], 
                            self.properties.DiscoverTime[v])
    
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

class StopAtVertex(CompositeVisitor):
    def __init__(self, agg, vset):
        CompositeVisitor.__init__(self, agg)
        self.vset = vset

    def discover_vertex(self, v):
        if v in self.vset:
            raise SuccessfulTraversal 


class AggregateVisitor(TraversalVisitor):
    def __init__(self, visitors, backend=None):
        TraversalVisitor.__init__(self)
        self.visit_order_dirty = True
        self.visitor_instances = {}
        self.visitors_by_name = {}
        self.visit_order = []
        self.backend = BackendCore() if backend is None else backend
        for visitor_type, args in visitors.items():
            self.add_visitor(visitor_type, args)
        self.compile_visit_order()
    
    def __ensure_visitor_instantiated(self, visitor_type, args):
        if visitor_type not in self.visitor_instances:
            if args is None:
                visitor_instance = visitor_type(self)
            else:
                visitor_instance = visitor_type(self, *args)
            self.visitor_instances[visitor_type] = visitor_instance
        return self.visitor_instances[visitor_type]

    def add_visitor(self, visitor_type, args):
        self.visit_order_dirty = True
        self.__ensure_visitor_instantiated(visitor_type, args)

    def compile_visit_order(self):
        self.visit_order = []
        self.visitors_by_name = {}
        for v in self.visitor_instances.values():
            self.__compute_dependencies(v)
        self.visit_order_dirty = False

    def __compute_dependencies(self, visitor):
        for dependency in visitor.dependencies:
            # Note implicit dependencies can't take arguments, since
            # there's no good way to specify them (they're implicit!)
            instance = self.__ensure_visitor_instantiated(dependency, None) 
            self.__compute_dependencies(instance)
        visitor_name = visitor.__class__.__name__
        if self.visitors_by_name.get(visitor_name) is None:
            self.visit_order.append(visitor)
            self.visitors_by_name[visitor_name] = visitor

    def __getattr__(self, name):
        visitor = self.visitors_by_name.get(name)
        if visitor is None:
            raise AttributeError(name)
        return visitor.value

    def start_traversal(self, v):
        if self.visit_order_dirty:
            self.compile_visit_order()
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


