import random
from itertools import islice, izip

from yaupon.data_structures.union_find import UnionFind
from yaupon.util.shortcuts import other_vertex
import yaupon.tree as tree


def matching(g):
    m = dict()
    while find_augmenting_path(g,m) is not None:
        pass
    return m


EVEN, ODD, UNREACHED = 0,1,2

def find_augmenting_path(g, initial_matching = None):
    vertex_state = dict()
    if initial_matching is None:
        matching = dict()
    else:
        matching = initial_matching
    even_edges = list()
    forest = tree.Forest(Vertices = g.vertices())
    blossoms = UnionFind(g.vertices())
    origin = dict((v,v) for v in g.vertices())
    bridge = dict()
        
    for v in g.vertices():
        if v not in matching:
            vertex_state[v] = EVEN
            for e in g.adjacent_edges(v):
                even_edges.append((v,other_vertex(e,v),e))
        else:
            vertex_state[v] = UNREACHED
            
    augmenting_path_edge = None
    while even_edges:
                
        u,v,current_edge \
           = even_edges.pop(int(random.uniform(0,len(even_edges))))
        u_prime = origin[blossoms.find(u)]
        v_prime = origin[blossoms.find(v)]
        
        if vertex_state[v_prime] == UNREACHED:
            vertex_state[v_prime] = ODD;
            v_prime_mate = other_vertex(matching[v_prime], v_prime)
            vertex_state[v_prime_mate] = EVEN;
            forest.add_edge(parent = u, 
                            child = v_prime, 
                            parent_edge = current_edge
                            )
            forest.add_edge(parent = v_prime, 
                            child = v_prime_mate, 
                            parent_edge = matching[v_prime]
                            )
            for e in g.adjacent_edges(v_prime_mate):
                even_edges.append((v_prime_mate,
                                   other_vertex(e,v_prime_mate),e))

        elif vertex_state[v_prime] == EVEN and u_prime != v_prime:
            try:
                nca = forest.nearest_common_ancestor(u_prime, v_prime)
            except tree.VertexNotFound:
                nca = None
            if nca is None:
                augmenting_path_edge = current_edge
                break
            for x in (u_prime, v_prime):
                prev_vertex = None
                for y in forest.get_tree(x).path_to_root():
                    if y == nca:
                        break
                    curr_vertex = origin[blossoms.find(y.vertex)]
                    if curr_vertex == prev_vertex:
                        continue
                    blossoms.link(curr_vertex, nca.vertex)
                    bridge[curr_vertex] = (x, current_edge)
                    prev_vertex = curr_vertex
            origin[blossoms.find(nca.vertex)] = nca.vertex
    
    def path(v,w):
        if v == w:
            return [v]
        v_mate = other_vertex(matching[v], v)
        if vertex_state[v] == EVEN:
            return [v, v_mate] + \
                   path(forest.get_tree(v_mate).parent().vertex, w)
        else: #vertex_state[v] == ODD
            x = bridge[v][0]
            y = other_vertex(bridge[v][1], bridge[v][0])
            return [v] + [i for i in reversed(path(x, v_mate))] + path(y,w)
    
    if augmenting_path_edge:
        x = g.source(augmenting_path_edge)
        y = g.target(augmenting_path_edge)
        x_up = path(x, forest.get_tree(x).get_root().vertex)
        y_up = path(y, forest.get_tree(y).get_root().vertex)
        print [i for i in reversed(x_up)] + y_up
        
        matching[g.source(augmenting_path_edge)] = augmenting_path_edge
        matching[g.target(augmenting_path_edge)] = augmenting_path_edge
        for path in (x_up,y_up):
            for x,y in izip(islice(path,1,None,2),islice(path,2,None,2)):
                matching[x] = matching[y] = forest.get_tree(x).parent_edge
        return matching
