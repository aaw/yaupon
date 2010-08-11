from yaupon.traversal.traversal import traverse
from yaupon.traversal.aggregate_visitor import AggregateVisitor, Parent
from yaupon.traversal.generators import best_first_generator

# The board is represented as a string of length 9, i.e.
#
#    +---+---+---+
#    | 0 | 1 | 2 |
#    +---+---+---+
#    | 3 | 4 | 5 |
#    +---+---+---+
#    | 6 | 7 |   |
#    +---+---+---+
#
# is represented by the string "01234567_"

# (x,y) means in tile y is in position x, want 
# to figure out contribution of position x

class manhattan_distance(object):
    def __getitem__(self, board):
        return sum(abs(i-int(x))%3 + abs(i-int(x))/3 \
                   for i,x in enumerate(board) if x != '_')


class tile_puzzle_graph:
    def edges(self, source):
        i = source.find('_')
        for compare, inc in [(i < 6, 3),      # tiles that can move down (+3) 
                             (i > 2, -3),     # tiles that can move up (-3)
                             (i % 3 > 0, -1), # tiles that can move left (-1)
                             (i % 3 < 2, 1)   # tiles that can move right (+1)
                             ]:
            if compare:
                l = list(source)
                l[i], l[i + inc] = l[i + inc], l[i]
                yield (source, ''.join(l))
            
            
def solve_tile_puzzle(board):
    parent_visitor = AggregateVisitor(visitors=[Parent])
    traverse(root_vertices = [board],
             visitor = parent_visitor, 
             generator = best_first_generator(tile_puzzle_graph(), 
                                              manhattan_distance())
             )
    return parent_visitor

def randomize_board(board, num_shuffles):
    import random
    for x in xrange(num_shuffles):
        i = board.find('_')
        possible_incs = []
        if i < 6: possible_incs.append(3)
        if i > 2: possible_incs.append(-3)
        if i % 3 > 0: possible_incs.append(-1)
        if i % 3 < 2: possible_incs.append(1)
        inc = random.sample(possible_incs,1)[0]
        l = list(board)
        l[i], l[i + inc] = l[i + inc], l[i]    
        board = ''.join(l)
    return board

if __name__ == '__main__':
    starting_board = randomize_board("01234567_", 10000)
    print 'Starting board is %s' % starting_board
    tree = solve_tile_puzzle(starting_board)
    print ''
    print 'PATH: '
    print ''

    path = []
    vertex = '01234567_'
    while vertex is not None:
        path.append(vertex)
        vertex = tree.Parent.get(vertex)

    for x in reversed(path):
        print ' %s\n %s\n %s\n' % (x[:3], x[3:6], x[6:])

    print '(%s steps)' % len(path)
