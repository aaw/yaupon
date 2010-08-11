from yaupon.backend import getbackend

def ydeque(backend, *args, **kwargs):
    return getbackend(backend).create_deque(*args, **kwargs)

def ydict(backend, *args, **kwargs):
    return getbackend(backend).create_dict(*args, **kwargs)

def ysorted(backend, *args, **kwargs):
    return getbackend(backend).sorted(*args, **kwargs)

def yheap(backend, *args, **kwargs):
    import yaupon.data_structures.dheap as dheap
    return dheap.DHeap(getbackend(backend), *args, **kwargs)

def yunion_find(backend, *args, **kwargs):
    import yaupon.data_structures.union_find as union_find
    return union_find.UnionFind(getbackend(backend), *args, **kwargs)
