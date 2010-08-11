import random

def shuffle_edges(g):
    """
    This function lets you randomly permute the vertices in a graph. Given a Graph
    g, you can create a Graph g2 with a permuted vertex set by using:
    g2 = Graph(Edges = shuffle_edges(g))
    """
    vertices = [v for v in g.vertices()]
    random.shuffle(vertices)
    perm = dict(zip(g.vertices(), vertices))
    edges = list()
    for e in g.edges():
        edges.append((perm[g.source(e)], perm[g.target(e)]))
    return edges


def add_random_edges(g, num_edges):
    edge_set = set()
    while len(edge_set) < num_edges:
        p = (random.randint(0,g.num_vertices()-1), random.randint(0,g.num_vertices()-1))
        if p[0] == p[1]:
            continue
        edge_set.add(p)
    for x in edge_set:
        ignore = g.add_edge(*x)
    return g

def make_d_regular_graph(g, degree):
    sample_space = dict((v, degree) for v in g.vertices())
    done = False
    while not done:        
        try:
            while sample_space:
                u,v = random.sample(sample_space.keys(), 2)
                g.add_edge(u, v)
                sample_space[u] -= 1
                sample_space[v] -= 1
                if sample_space[u] == 0:
                    del sample_space[u]
                if sample_space[v] == 0:
                    del sample_space[v]
        except:
            sample_space = dict((v, degree) for v in g.vertices())
            g.clear_edges()
        else:
            done = True
    return g