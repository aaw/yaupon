import exceptions

class AlgorithmError(Exception):
    pass

class NoIndegreeZeroVertices(AlgorithmError): pass

class NoIsomorphismExists(AlgorithmError): pass

class CycleExists(AlgorithmError): pass

class NegativeCycleError(AlgorithmError):
    def __init__(self, cycle = None):
        self.cycle = cycle

class NegativeEdgeWeightError(AlgorithmError):
    def __init__(self, edge):
        self.edge = edge
    def __str__(self):
        return repr(self.edge)


