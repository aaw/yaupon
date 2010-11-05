import yaupon.algorithm.detail.isomorphism as backtracking_isomorphism
from yaupon.algorithm.exceptions import NoIsomorphismExists


class isomorphism(object):
    def __init__(self, description):
        self.description = description

    def compile(self, g1, g2):
        self.iso = backtracking_isomorphism.isomorphism(g1,g2)
        if self.iso is None:
            raise NoIsomorphismExists

    def __getitem__(self, key):
        return self.iso[key]
        

def compile(graph1, graph2):
    algorithm = isomorphism('backtracking_isomorphism')
    algorithm.compile(graph1, graph2)
    return algorithm
