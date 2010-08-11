from collections import defaultdict

from yaupon.tests.testutils import graph_database_iteration
import yaupon.algorithm.shortest_path as shortest_path


def pytest_generate_tests(metafunc):
    graph_database_iteration(metafunc)

def test_shortest_paths(graph):
    """
    A tree T plus an edge_weight map W is a shortest path tree for
    graph G exactly when, for every edge e in G.edges(),
    
        sum(W[f] for f in T.path_to_root(e[0])) + W[e]
        >=
        sum(W[f] for f in T.path_to_root(e[1]))

    verify_shortest_path_tree tests this relationship. If there's an 
    edge that violates this relationship, that edge is returned. 
    Otherwise, None is returned.
    """    
    g = graph()
    edge_weight = getattr(g, 'edge_weight', None)
    ew = edge_weight if edge_weight is not None else defaultdict(int)
    for v in g.vertices():
        sp = shortest_path.compile(graph=g, edge_weight=edge_weight, target=v)
        for e in g.edges():
            assert sum(ew[f] for f in sp(source=e[0])) + ew[e] >= \
                   sum(ew[f] for f in sp(source=e[1]))
