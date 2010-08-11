import sys
import itertools
import yaupon

def read_dimacs(f = sys.stdin,
                GraphType = yaupon.Graph
                ):
    
    for line in f:
        line = line.strip()
        
        if not line or line[0] == 'c':
            continue
        
        if line[0] == 'p':
            ignore, format, nodes, edges = line.split(' ')
            if format == 'edge':
                return parse_edge_format(f, GraphType)
            elif format == 'sp':
                return parse_sp_format(f, GraphType)
            elif format == 'min':
                #Not yet implemented...
                return parse_min_format(f, GraphType)
            
            
            
def parse_edge_format(f, GraphType):
            
    g = GraphType()
    for line in f:
        line = line.strip()
        
        if not line or line[0] == 'c':
            continue
            
        if line[0] == 'e':
            ignore, source, target = line.split(' ')
            g.add_edge(int(source), int(target))
            
    return g




def parse_sp_format(f, GraphType):
    
    g = GraphType()
    g.make_property('edge_weight')
    
    for line in f:
        line = line.strip()
    
        if not line or line[0] == 'c':
            continue
        
        if line[0] == 'a':
            ignore, source, target, weight = line.split(' ')
            g.edge_weight[g.add_edge(int(source),int(target))] = int(weight)
             
    return g



def write_dimacs(g, 
                 f = sys.stdout,
                 type = EDGE,
                 comment = None                   	
                 ):
    
    if comment is not None:
        f.write('c %s\n\n' % comment)

    n_vertices = sum(1 for v in g.vertices())
    n_edges = sum(1 for e in g.edges())
    f.write('p edge %s %s\n' % (n_vertices, n_edges))

    vertex_to_index = dict()
    next_index = 1
    for vertex in g.vertices():
        vertex_to_index[vertex] = next_index
        next_index += 1
    
    for s, t in g.edges():
        f.write('e %s %s\n' % (vertex_to_index[s], vertex_to_index[t]))
