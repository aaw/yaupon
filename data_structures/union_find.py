from yaupon.data_structures import ydict
from yaupon.backend import BackendCore

class UnionFind(object):
    
    def __init__(self, backend=None):
        self.__backend = BackendCore() if backend is None else backend
        self.__parent = ydict(backend=backend)
        self.__rank = ydict(backend=backend)

    def __backend__(self):
        return self.__backend
        
    def find(self, x):
        """
        Find the canonical item of the set containing x. Uses path halving.
        """
        x_parent = self.__parent.get(x)
        if x_parent is None:
            self.__parent[x] = x
            self.__rank[x] = 0
            return x
        
        while self.__parent[x_parent] != x_parent:
            grandparent = self.__parent[x_parent]
            self.__parent[x] = grandparent
            x = grandparent
            x_parent = self.__parent[x]
        return x_parent

    def link(self, x, y):
        """
        Link the set that contains x with the set that contains y. If x
        and y are already in the same set, returns None. Otherwise, returns
        the new canonical element of the set containing both x and y
        """
        x = self.find(x)
        y = self.find(y)
        if x == y:
            return None
        
        if self.__rank[x] > self.__rank[y]:
            x, y = y, x
        elif self.__rank[x] == self.__rank[y]:
            self.__rank[y] = self.__rank[y] + 1
        self.__parent[x] = y
        return y
    
