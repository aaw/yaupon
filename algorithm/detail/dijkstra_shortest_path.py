from yaupon.algorithm.exceptions import NegativeEdgeWeightError
from yaupon.data_structures import ydict, yheap
from yaupon.util.shortcuts import other_vertex

def make_tree(graph, source, edge_weight = None):
    parent = ydict(backend=graph)
    heap = yheap(backend=graph)
    distance = ydict(backend=graph)
    
    u, distance[u] = source, 0
    while True:
        for e in graph.edges(source = u):
            if edge_weight[e] < 0:
                raise NegativeEdgeWeightError(e)
            v = other_vertex(e,u)
            distance_to_v = distance.get(v)
            relaxed_length = distance[u] + edge_weight[e]
            if distance_to_v is None or relaxed_length < distance_to_v:
                parent[v] = e
                distance[v] = relaxed_length
                if v in heap:
                    heap.modifykey(v, relaxed_length)
                else:
                    heap.insert(v, relaxed_length)

        try:
            u = heap.deletemin()
        except:
            return parent

