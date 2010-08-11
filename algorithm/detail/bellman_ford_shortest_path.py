from yaupon.algorithm.exceptions import NegativeCycleError
from yaupon.data_structures import ydict, ydeque
from yaupon.util.shortcuts import other_vertex

# Currently using pass counting to detect negative cycles; doing this 
# requires an iteration over all vertices up front to know #(V(G)), 
# but Tarjan describes another way by carefully inspecting children in
# the shortest path tree

def make_tree(graph, source, edge_weight = None):
    parent = ydict(backend=graph)
    distance = ydict(backend=graph)
    queue = ydeque(backend=graph)
    queue_members = ydict(backend=graph)

    queue.append(source)
    queue_members[source] = True
    distance[source] = 0
    curr_pass = 0
    curr_last = source

    num_vertices = sum(1 for v in graph.vertices())

    while queue:
        v = queue.popleft()
        del queue_members[v]
        for e in graph.edges(source = v):
            w = other_vertex(e, v)
            dw, dv, e_weight = distance.get(w), distance[v], edge_weight[e]
            if dw is None or dv + e_weight < dw:
                distance[w] = dv + e_weight
                parent[w] = e
                if w not in queue_members:
                    queue.append(w)
                    queue_members[w] = True
        if v == curr_last and queue:
            curr_pass += 1
            curr_last = queue[-1]
        if curr_pass >= num_vertices:
            raise NegativeCycleError
    return parent

