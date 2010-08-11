import copy
import graph.algorithm.detail.traversal as traversal
import graph.algorithm.detail.strategy as strategy
import graph.algorithm.detail.visitor as visitor

dontcares = '._-0'

peers = dict()
for i in xrange(81):
    peerset = set()
    peerset.update(xrange(i - i%9,i - i%9 + 9))
    peerset.update(xrange(i%9,81,9))
    rc, cc = i/9/3, i%9/3
    for z in xrange(0,27,9):
        peerset.update(xrange(rc*27 + cc*3 + z, rc*27 + cc*3 + z + 3))
    peerset.remove(i)
    peers[i] = peerset


def make_board(description):
    board = dict([(i,set(xrange(1,10))) for i in xrange(81)])
    for i,val in enumerate(description):
        if val not in dontcares and not propagate(board,i,int(val)):
            return dict()
    return board


def make_desc(board):	
    desc = ''
    for key,val in sorted(board.iteritems()):
        if len(val) == 1:
	    s = copy.deepcopy(val)
	    desc += str(s.pop())
        else:
            desc += '.'
    return desc


def propagate(board, position, val):
    board[position] = set([val])
    for peer in peers[position]:
        prev_size = len(board[peer])
        if val in board[peer]:
            board[peer].remove(val)
        if len(board[peer]) == 0:
            return False
        elif len(board[peer]) == 1 and prev_size == 2:
            propagate(board, peer, board[peer].pop())
    return True

def mykey(x):
    k,v = x
    return len(v) if len(v) > 1 else 11

class sudoku_graph:
    def adjacent_edges(self, v):
        b = make_board(v)
        if len(b) == 0:
            return
        for i,allowed in sorted(b.iteritems(), key = mykey):
            if len(allowed) > 1:
                for z in allowed:
                    b2 = make_board(v)
                    if propagate(b2, i, z):
                        yield (v, make_desc(b2))
                break

class sudoku_visitor(visitor.visitor):
    def visit_vertex(self, v):
        result = sum(v.find(dontcare) for dontcare in dontcares)
        if result == -len(dontcares):
            print 'FOUND SOLUTION! %s\n\n' % v
	    for r in range(9):
                print v[r*9:r*9+9]
	    raise StandardError
