from yaupon.data_structures import ydict
from yaupon.algorithm.detail.fruchterman_reingold import fruchterman_reingold_drawing

class force_directed_layout(object):
    def __init__(self, graph):
        self.graph = graph

    def __call__(self, width=None, height=None):
        if width is None:
            width = 400
        if height is None:
            height = 400
            p = ydict(memory_usage=self.graph.MemoryUsage)
            p = fruchterman_reingold_drawing(self.graph, position = p, 
                                             min_x = 10, max_x = width + 10, 
                                             min_y = 10, max_y = height + 10,
                                             iterations = 500, temp = 100, 
                                             cool = lambda t : max(0, t - 0.1))
            p = fruchterman_reingold_drawing(self.graph, position = p, 
                                             min_x = 10, max_x = width + 10, 
                                             min_y = 10, max_y = height + 10,
                                             iterations = 100, temp = 20, 
                                             cool = lambda t : max(0, t - 1))
            return p

def compile(graph):
    return force_directed_layout(graph)
    
