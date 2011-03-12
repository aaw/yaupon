from yaupon.data_structures import ydeque, ydict
from yaupon.traversal import *

class StronglyConnectedComponents(object):
    def __init__(self, graph):
        self.description = 'Forest isomorphism'
        generator = depth_first_generator(graph)
        visitor = AggregateVisitor(backend=graph, 
                                   visitors={Depth:None}) 
        traverse(root_vertices=graph.vertices(),
                 visitor=visitor,
                 generator=depth_first_generator(graph))
        self.depth = visitor.Depth

    def __call__(self, v):
        pass

