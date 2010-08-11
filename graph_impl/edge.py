class TupleFactory(object):

    def __call__(source, target, id):
        return (source, target)

class MultiEdge(object):

    IsMultiEdgeCompatible = True
    next_id = 0

    def __init__(self, source, target, id = None):
        self.source = source
        self.target = target
        if id is None:
            id = MultiEdge.next_id
            MultiEdge.next_id += 1
        self.id = id

    def __str__(self):
        return '(%s,%s)' % (self.source, self.target)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        self.__index = -1
        return self
    
    def next(self):
        self.__index += 1
        if self.__index == 0:
            return self.source
        elif self.__index == 1:
            return self.target
        else:
            raise StopIteration

    def __getitem__(self, index):
        if index == 0: return self.source
        if index == 1: return self.target
        raise IndexError

    def __cmp__(self, other):
        other_id = getattr(other, 'id', None)
        return cmp(self.id, other_id)

    def __hash__(self):
        return self.id
