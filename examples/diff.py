import graph.algorithm.shortest_path as shortest_path

"""
An implementation of the diff of two sequences
""" 

class diff_graph(object):
    
    def __init__(self, seq1, seq2):
        self.x_vertices = seq1
        self.y_vertices = seq2
    
    def edges(self, source):
        x,y = source
        can_inc_x = x < len(self.x_vertices) - 1
        can_inc_y = y < len(self.y_vertices) - 1
        if can_inc_x:
            yield ((x,y),(x+1,y))
        if can_inc_y:
            yield ((x,y),(x,y+1))
        if can_inc_x and can_inc_y and \
           self.x_vertices[x+1] == self.y_vertices[y+1]:
            yield ((x,y),(x+1,y+1))


class diff_edge_weight(object):    
    def __getitem__(self, edge):
        return 0 if edge[0][0] < edge[1][0] and edge[0][1] < edge[1][1] else 1
        

def diff(seq1, seq2):
    path_from_origin = shortest_path.Oracle(graph = diff_graph(seq1, seq2), 
                                            edge_weight = diff_edge_weight(),
                                            source = (-1,-1)
                                            )
    
    print_gnu_diff_output(seq1, seq2, path_from_origin.edges((len(seq1)-1, len(seq2)-1)))



# The function print_gnu_diff_output just pretty-prints the edit script so that
# it looks similar to the output you get from using gnu diff.
    
def print_gnu_diff_output(list1, list2, edit_path):
    edit_commands = list()
    current_command_start = None
    for edge in edit_path:
        x_increased = edge[0][0] < edge[1][0]
        y_increased = edge[0][1] < edge[1][1]
        if not (x_increased and y_increased) and current_command_start is None:
            current_command_start = edge[0]
        if x_increased and y_increased and current_command_start is not None:
            edit_commands.append((current_command_start, edge[0]))
            current_command_start = None
    if current_command_start is not None:
        edit_commands.append((current_command_start, edge[1]))
            
    for command in edit_commands:
        (x1,y1),(x2,y2) = command
        if x1 < x2 and y1 < y2:
            command_name = 'c'
        elif x1 < x2:
            command_name = 'd'
        else:
            command_name = 'a'

        range_1_text = str(x2+1) if x2 - x1 < 2 else '%s,%s' % (x1+2,x2+1)
        range_2_text = str(y2+1) if y2 - y1 < 2 else '%s,%s' % (y1+2,y2+1)

        print '%s%s%s' % (range_1_text, command_name, range_2_text)
        if command_name in ('c','d'):
            for data in list1[x1+1:x2+1]:
                print ('< %s' % data).rstrip()
        if command_name == 'c':
            print '---'
        if command_name in ('c','a'):
            for data in list2[y1+1:y2+1]:
                print ('> %s' % data).rstrip()
    
    print ''
