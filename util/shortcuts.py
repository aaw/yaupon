
def other_vertex(e, v):
    return e[0] if e[0] != v else e[1]

def reverse_edge(e):
    return type(e)(source=e[1], target=e[0], id=e.id)

def sources(g):
    for v in g.vertices():
        try:
            g.edges(target=v).next()
        except StopIteration:
            yield v

def sinks(g):
    for v in g.vertices():
        try:
            g.edges(source=v).next()
        except StopIteration:
            yield v
