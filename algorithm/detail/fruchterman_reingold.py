import math
import random
from yaupon.data_structures import map

def norm(vector):
    return math.sqrt(sum(x*x for x in vector))

def tuple_op(vector1, vector2, op):
    return (op(vector1[0],vector2[0]), op(vector1[1],vector2[1]))

def repel(u, v_pos, f_r, position, displacement, div_floor):
    delta = tuple_op(position[u], v_pos, lambda x,y: x - y)
    delta_norm = max(norm(delta), div_floor)
    res = tuple_op(delta, (delta_norm, delta_norm), lambda x,y: x/y)
    f_r_result = f_r(delta_norm)
    res = tuple_op(res, (f_r_result, f_r_result), lambda x,y: x * y)
    displacement[u] = tuple_op(displacement[u], res, lambda x,y: x + y)

def fruchterman_reingold_drawing(g, min_x = 0, max_x = 100, min_y = 0, max_y = 100, f_a = None, f_r = None, 
                                 position = None, iterations = 50, temp = 25, cool = None, 
                                 div_floor = 0.01):
    height = max_y - min_y
    width = max_x - min_x
    area = height * width
    if cool is None:
        cool = lambda t : max(t - 0.1, 0)
    if position is None:
        position = map(memory_usage=g.MemoryUsage)
    displacement = map(memory_usage=g.MemoryUsage)
    num_vertices = 0
    for v in g.vertices():
        num_vertices += 1
        displacement[v] = (0,0)
        if position.get(v) is None:
            position[v] = (random.randint(-width/2,width/2), random.randint(-height/2,height/2))
    k = math.sqrt(area / num_vertices)
    if f_a is None:
        f_a = lambda x: x * x / k
    if f_r is None:
        f_r = lambda x: k * k / x 

    for i in xrange(iterations):

        # Calculate repellent forces
        for u in g.vertices():
            for v in g.vertices():
                if u == v:
                    continue
                repel(u, position[v], f_r, position, displacement, div_floor)
        
        # Calculate attractive forces
        for u,v in g.edges():
            delta = tuple_op(position[v], position[u], lambda x,y: x - y)
            delta_norm = max(norm(delta), div_floor)
            res = tuple_op(delta, (delta_norm, delta_norm), lambda x,y: x/y)
            f_a_result = f_a(delta_norm)
            res = tuple_op(res, (f_a_result, f_a_result), lambda x,y: x * y)
            displacement[v] = tuple_op(displacement[v], res, lambda x,y: x - y)
            displacement[u] = tuple_op(displacement[u], res, lambda x,y: x + y )

        # attract everything to the center
        for v in g.vertices():
            delta = tuple_op(position[v], (0,0), lambda x,y: x - y)
            delta_norm = max(norm(delta), div_floor)
            res = tuple_op(delta, (delta_norm, delta_norm), lambda x,y: x/y)
            f_a_result = 1.5 * f_a(delta_norm)
            res = tuple_op(res, (f_a_result, f_a_result), lambda x,y: x * y)
            displacement[v] = tuple_op(displacement[v], res, lambda x,y: x - y)

        # Update position using displacement
        for v in g.vertices():
            disp_norm = max(norm(displacement[v]), div_floor)
            # TODO: can avoid these steps if disp_norm < temp
            v_pos_addend = tuple_op(displacement[v], (disp_norm, disp_norm), lambda x,y: x / y)
            v_pos_addend = tuple_op(v_pos_addend, (min(disp_norm, temp), min(disp_norm, temp)), 
                                    lambda x,y: x * y)
            position[v] = tuple_op(position[v], v_pos_addend, lambda x,y: x + y)
            wfuzz = random.randint(5,int(width/8.0))
            hfuzz = random.randint(5,int(height/8.0))
            position[v] = (min(width/2 - wfuzz, max(-width/2 + wfuzz, position[v][0])), 
                           min(height/2 - hfuzz, max(-height/2 + hfuzz, position[v][1])))

        temp = cool(temp)

    for v in g.vertices():
        old_pos = position[v]
        position[v] = (old_pos[0] + width/2 + min_x, old_pos[1] + height/2 + min_y)
    return position

if __name__ == '__main__':
    import yaupon
    import sys
    from yaupon.plotters.svg_plotter import plot
    
    if len(sys.argv) > 1 and sys.argv[1] == 'K_5':
        # K_5
        g = yaupon.Graph(edges = [(i,j) for i in xrange(5) for j in xrange(5) if i < j])
    elif len(sys.argv) > 1 and sys.argv[1] == 'planar':
        g = yaupon.Graph(edges = [(0,1),(1,2),(2,3),(3,0),(0,5),(5,1),(1,6),(6,7),(7,3)])
    else:
        g = yaupon.Graph(edges = [(i,i+1) for i in xrange(5)])
        g.add_edge(0,5)
        g.add_edge(0,6)
        g.add_edge(0,7)
        g.add_edge(2,8)
        g.add_edge(8,9)
        g.add_edge(8,10)
        g.add_edge(8,11)
        for i in xrange(12,20):
            g.add_edge(3,i)

    p = g.make_vertex_property()
    p = fruchterman_reingold_drawing(g, position = p, min_x = 10, max_x = 410, min_y = 10, max_y = 410,
                                     iterations = 500, temp = 100, 
                                     cool = lambda t : max(0, t - 0.1))
    p = fruchterman_reingold_drawing(g, position = p, min_x = 10, max_x = 410, min_y = 10, max_y = 410,
                                     iterations = 100, temp = 20, 
                                     cool = lambda t : max(0, t - 1))
    f = open('test.svg', 'w')
    plot(graph = g, position = p, f = f)
    f.close()
