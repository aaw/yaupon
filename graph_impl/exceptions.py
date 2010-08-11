import exceptions

class GraphConstructionError(Exception):
    pass

class CycleCreatedError(GraphConstructionError):
    def __init__(self, cycle):
        self.cycle = cycle
    def __str__(self):
        return repr(self.cycle)

class VertexNotFoundError(GraphConstructionError):
    def __init__(self, vertex):
        self.vertex = vertex
    def __str__(self):
        return repr(self.vertex)

class NoPathExistsError(GraphConstructionError):
    pass
