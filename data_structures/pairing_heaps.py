import yaupon
from itertools import tee, izip_longest, islice

def takepairs(iterator):
    """
    Transforms a sequence x1, x2, x3, x4, x5 into a sequence
    of pairs: (x1, x2), (x3, x4), (x5, None)
    """
    a, b = tee(iterator)
    return izip_longest(islice(a, 0, None, 2), islice(b, 1, None, 2))

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
    
    def __link(self, x):
        if self.head is None:
            self.head = x
            return
        xrec, hrec = self.nodes[x], self.nodes[self.head]
        if self.cmp(hrec[KEY], xrec[KEY]) <= 0:
            if hrec[CHILD] is None:
                xrec[PARENT] = self.head
            xrec[SIBLING] = hrec[CHILD]
            hrec[CHILD] = x
            self.nodes[x], self.nodes[self.head] = xrec, hrec
        else:
            if xrec[CHILD] is None:
                hrec[PARENT] = x
            hrec[SIBLING] = xrec[CHILD]
            xrec[CHILD] = self.head
            self.nodes[x], self.nodes[self.head] = xrec, hrec
            self.head = x

    def insert(self, item, key=None):
        self.__initialize(item, key)
        self.__link(item)

    def findmin(self):
        return self.head

    def findminkey(self):
        return self.nodes[self.head][KEY]

    def deletemin(self):
        pass

    def meld(self, other):
        pass

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
        self.__link(item)

    def getkey(self, item):
        return self.nodes[item][KEY]

    def __contains__(self, item):
        return item in self.nodes
            
