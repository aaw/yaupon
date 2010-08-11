graph_memory_usage = 'CORE' 

def dispatch_graph(*args, **kwargs):
    if graph_memory_usage == 'CORE':
        import graph_impl.dictgraph
        return graph_impl.dictgraph.DictGraph(*args, **kwargs)
    elif graph_memory_usage == 'EXTERNAL':
        import graph_impl.sqlitegraph
        return graph_impl.sqlitegraph.SQLiteGraph(*args, **kwargs)

def dispatch_forest(*args, **kwargs):
    import graph_impl.forest
    return graph_impl.forest.Forest(*args, **kwargs)

