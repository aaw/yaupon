from yaupon.data_structures.union_find import UnionFind
from yaupon.data_structures.dheap import DHeap

def spanning_tree_edges(graph, edge_weight):
    components = UnionFind(memory_usage=graph.MemoryUsage)
    sorted_edges = DHeap(memory_usage=graph.MemoryUsage)
    for edge in graph.edges():
        sorted_edges.insert(edge, key=edge_weight[edge])

    while sorted_edges:
        edge = sorted_edges.deletemin()
        if components.link(*edge) is not None:
            yield edge
