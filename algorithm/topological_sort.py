from yaupon.data_structures import ydeque, ydict
from yaupon.traversal import *
from yaupon.algorithm.exceptions import NoIndegreeZeroVertices, CycleExists

class dfs_topological_sort(object):
    def __init__(self, graph):
        self.description = 'depth-first search topological sort'
        finished_vertices = ydict(backend=graph)
        generator = depth_first_generator(graph)

        # Bootstrap the depth-first search generator with all vertices
        # of indegree 0. If there are no such vertices, raise an exception.
        found_starting_vertex = False
        for v in graph.vertices():
            try:
                graph.edges(target=v).next()
            except StopIteration:
                generator.bootstrap(v)
                found_starting_vertex = True
        if not found_starting_vertex:
            raise NoIndegreeZeroVertices

        # Topological ordering is now the reverse of the postorder. But
        # a topological ordering still might not be possible if there are
        # cycles, so we'll check for those here and raise an exception
        # if there is one.
        self.topological_order = ydeque(backend=graph)
        # TODO: don't use the generator directly here, use a visitor
        for e in generator.events():
            if e['type'] == 'VERTEX' and e['state'] == 'FINISHED':
                self.topological_order.append(e['vertex'])
            elif e['type'] == 'EDGE' and e['target_state'] == 'DISCOVERED':
                raise CycleExists

    def __call__(self):
        #TODO: need reversed iterator for SQLiteDeque
        return reversed(self.topological_order)

def compile(graph):
    return dfs_topological_sort(graph)

