import yaupon
from yaupon.traversal import *

def test_line_graph(size = 10):
    """
    On a line graph, dfs should enumerate vertices consecutively
    """
    g = yaupon.Graph(edges = [(i,i+1) for i in xrange(size-1)])
    for v in g.vertices():
        visitor = AggregateVisitor(visitors=[DiscoverTime])
        traverse([v], visitor, depth_first_generator(g))
        for i in xrange(size - 1):
            if i >= v:
                assert visitor.DiscoverTime[i] <= visitor.DiscoverTime[i+1]

def test_forks():
    """
    This test makes a graph that looks like:

        *--*
       /
      *--*--*
       \
        *--*
    
    and then verifies some properties of depth first search
    """
    g = yaupon.Graph()
    root = g.add_vertex()
    u2, u3 = g.add_vertex(), g.add_vertex()
    g.add_edge(root,u2)
    g.add_edge(u2,u3)
    v2, v3 = g.add_vertex(), g.add_vertex()
    g.add_edge(root,v2)
    g.add_edge(v2,v3)
    w2, w3 = g.add_vertex(), g.add_vertex()
    g.add_edge(root,w2)
    g.add_edge(w2,w3)

    visitor = AggregateVisitor(visitors=[Parent])
    traverse([root], visitor, depth_first_generator(g))
    assert visitor.Parent[u2] == root
    assert visitor.Parent[u3] == u2
    assert visitor.Parent[v2] == root
    assert visitor.Parent[v3] == v2
    assert visitor.Parent[w2] == root
    assert visitor.Parent[w3] == w2

#TODO: parameterize this test, it's true of any graph and DFS
def test_graph_splits():
    """
    In any depth-first search tree, any edge (root, X) in
    the depth-first search tree partitions the graph: there
    are no edges between any vertex visited before X and any
    vertices visited after X in the original graph.
    """
    g = yaupon.Graph(edges = [(0,1),(2,3),(3,4),(1,2),(0,3),(4,5),
                              (5,9),(1,4),(4,6),(6,1),(1,3),(6,7),
                              (7,0),(9,8),(8,3),(0,10),(10,11),(11,12),
                              (0,13),(13,14),(14,15),(15,13),(14,13)])
    visitor = AggregateVisitor(visitors=[Parent, ParentEdge, DiscoverTime])
    traverse([0], visitor, depth_first_generator(g))
    root_edges = [visitor.ParentEdge[v] for v in g.vertices() \
                  if v != 0 and visitor.Parent[v] == 0] 
    for x,y in root_edges:
        before = [v for v in g.vertices() \
                  if visitor.DiscoverTime[v] < visitor.DiscoverTime[y] and \
                     v != 0]
        after = [v for v in g.vertices() \
                 if visitor.DiscoverTime[v] > visitor.DiscoverTime[y]]
        for b in before:
            for a in after:
                assert [e for e in g.edges(b,a)] == []

