from yaupon.data_structures import ydict, ydeque, ysorted
from yaupon.traversal import *

def forest_isomorphism(f1, f2):
    #TODO: do this at a higher level, since both iso testers need it
    if sum(1 for v in f1.vertices()) != sum(1 for v in f2.vertices()) or \
       sum(1 for e in f1.edges()) != sum(1 for e in f2.edges()):
        return None

    results = []
    for forest in (f1,f2):
        generator = depth_first_generator(forest)
        visitor = AggregateVisitor(backend=forest, 
                                   visitors={Depth:None}) 
        traverse(root_vertices=graph.vertices(),
                 visitor=visitor,
                 generator=depth_first_generator(forest))
        results.append(visitor.Depth)
    f1_depth, f2_depth = results

    f1_by_depths = ydict(backend=f1)
    f2_by_depths = ydict(backend=f2)
    max_depth = 0
    for forest, depth, index_by_depths in [(f1, f1_depth, f1_by_depths),
                                           (f2, f2_depth, f2_by_depths)]:
        for v in forest.vertices():
            d = depth[v]
            max_depth = max(d, max_depth)
            index_by_depths[d] = index_by_depths.setdefault(d, ydeque(backend=forest)).append(v)
            
    prev_f1_canonical_id = ydict(backend=f1)
    prev_f2_canonical_id = ydict(backend=f2)
    if len(f1_by_depths[max_depth]) != len(f2_by_depths[max_depth]):
        return
    for v in f1_by_depths[max_depth]:
        prev_f1_canonical_id[v] = 0
    for v in f2_by_depths[max_depth]:
        prev_f2_canonical_id[v] = 0

    for depth in xrange(max_depth - 1, -1, -1):
        f1_vertex_id = ydict(backend=f1)
        f2_vertex_id = ydict(backend=f2)
        if len(f1_by_depths[depth]) != len(f2_by_depths[depth]):
            return
        # don't do two-phase canonical id -> id transformation. instead, compute canonical ids
        # on the fly by storing a lexicographically sorted list of ids and binary searching for
        # existing ids each time
        for v in f1_by_depths[depth]:
            f1_vertex_id[v] = ydeque(backend=f2_vertex_id,
                                     ysorted(backend=f2_vertex_id,
                                             (prev_f1_canonical_id[w] for u,w in f1.edges(source=v))))
        for v in f2_by_depths[depth]:
            f2_vertex_id[v] = ydeque(backend=f2_vertex_id,
                                     ysorted(backend=f2_vertex_id,
                                             (prev_f2_canonical_id[w] for u,w in f2.edges(source=v))))

