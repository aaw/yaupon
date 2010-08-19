import yaupon
from itertools import tee, izip_longest, islice

def takepairs(iterator):
    """
    Transforms a sequence x1, x2, x3, x4, x5 into a sequence
    of pairs: (x1, x2), (x3, x4), (x5, None)
    """
    a, b = tee(iterator)
    return izip_longest(islice(a, 0, None, 2), islice(b, 1, None, 2))

def takeconjoinedpairs(iterator):
    """
    Transforms a sequence x1, x2, x3, x4, x5 into a sequence
    of pairs: (x1, x2), (x2, x3), (x3, x4), (x4, x5)
    """
    a, b = tee(iterator)
    return izip(islice(a, 0, None), islice(b, 1, None))

CHILD, SIBLING, PARENT, KEY = 0, 1, 2, 3

class PairingHeap(object):
    def __init__(self, backend=None, cmp=cmp):
        self.nodes = yaupon.ydict(backend=backend)
        # 'nodes' maps item -> [child, sibling, parent, key] 
        self.cmp = cmp
        self.head = None

    def __initialize(self, item, key=None):
        if key is None:
            key = item
        self.nodes[item] = [None, None, None, key]

    def __getparent(self, x):
        while self.nodes[x][SIBLING] is not None:
            x = self.nodes[x][SIBLING]
        return self.nodes[x][PARENT]

    def __getchildren(self, x):
        x = self.nodes[x][CHILD]
        while x is not None:
            yield x
            x = self.nodes[x][SIBLING]
    
    def __link(self, x, y):
        xrec, yrec = self.nodes[x], self.nodes[y]
        if self.cmp(xrec[KEY], yrec[KEY]) > 0:
            x, y, xrec, yrec = y, x, yrec, xrec
        if xrec[CHILD] is None:
            yrec[PARENT] = x
        yrec[SIBLING] = xrec[CHILD]
        xrec[CHILD] = y
        self.nodes[x], self.nodes[y] = xrec, yrec
        return x

    def insert(self, item, key=None):
        self.__initialize(item, key)
        if self.head is None:
            self.head = item
        else:
            self.head = self.__link(item, self.head)

    def findmin(self):
        return self.head

    def findminkey(self):
        return self.nodes[self.head][KEY]

    def deletemin(self):
         old_head = self.head
        to_merge = []
        for first, second in takepairs(self.__getchildren(old_head)):
            if second is None:
                to_merge.append(first)
                continue
            to_merge.append(self.__link(first, second))
        #TODO: implement __reversed__ for sqlitedeque
        if not to_merge:
            new_head = None
        else:
            new_head = to_merge[0]
            for first, second in takeconjoinedpairs(reversed(to_merge)):
                new_head = self.__link(first, second)
        # Replace self.head
        self.head = new_head
        del self.nodes[old_head]
        if new_head is not None:
            self.nodes[self.head][PARENT] = None
        return old_head

    def meld(self, other):
        self.nodes.update(other.nodes)
        self.head = self.__link(self.head, other.head)

    def modifykey(self, item, newkey):
        rec = self.nodes[item]
        if item == self.head:
            rec[KEY] = newkey
            self.nodes[item] = rec
            return

        # Splice item out of its parent's child list
        p = self.__getparent(item)
        prec = self.nodes[p]
        if prec[CHILD] == item: # item is first child of parent
            prec[CHILD] = rec[SIBLING]
            self.nodes[p] = prec
        else: # item is second child or later or parent
            itr = prec[CHILD]
            irec = self.nodes[itr]
            while irec[SIBLING] != item:
                itr = irec[SIBLING]
                irec = self.nodes[itr]
            irec[SIBLING], irec[PARENT] = rec[SIBLING], rec[PARENT]
            self.nodes[itr] = irec
        rec[SIBLING], rec[PARENT], rec[KEY] = None, None, newkey
        self.nodes[item] = rec
                    
        # Re-insert item
        self.head = self.__link(self.head, item)

    def getkey(self, item):
        return self.nodes[item][KEY]

    def __contains__(self, item):
        return item in self.nodes
            
