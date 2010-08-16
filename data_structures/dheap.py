import math

from yaupon.backend import BackendCore
from yaupon.data_structures import ydeque, ydict

def supermin(iterable, cmp=cmp, key=None):
    if key is None:
        key = lambda x : x
    curr_min = None
    for x in iterable:
        if curr_min is None or cmp(key(x), key(curr_min)) < 0:
            curr_min = x
    return curr_min

class DHeap(object):

    def __init__(self, 
                 backend, 
                 items=None,
                 d=3,
                 cmp=cmp,
                 key=None):
        self.__backend = backend
        self.__d = d
        self.cmp = cmp
        self.key = ydict(backend=self.__backend)
        self.__heap_index = ydict(backend=self.__backend)
        if key is not None:
            for k,v in key.iteritems():
                self.key[k] = v
        self.__heap = ydeque(backend=self.__backend)
        if items is not None:
            for item in items:
                self.__heap.append(item)
                if item not in self.key:
                    self.key[item] = item
            self.__heapify()

    def __heapify(self):
        for x in range(len(self.__heap) - 1, -1, -1):
            self.__siftdown(self.__heap[x], x)
        
    def __len__(self):
        return len(self.__heap)
        
    def __iter__(self):
        return self.__heap.__iter__()
        
    def __parent(self, x):
        return None if x == 0 else int(math.ceil((x-1)/self.__d))
    
    def __first_child(self, x):
        return self.__d*x + 1
    
    def __children(self, x):
        start = self.__first_child(x)
        end = min(self.__first_child(x+1), len(self.__heap))
        return None if start > end else range(start,end)

    def __min_child(self, pos):
        children = self.__children(pos)
        return None if not children else \
               supermin(children,
                        key=lambda x : self.key[self.__heap[x]],
                        cmp=self.cmp)

    def __update_index(self, pos):
        self.__heap_index[self.__heap[pos]] = pos
    
    def __siftup(self, item, pos = None):
        if pos is None:
            pos = self.__heap_index[item]
        parent = self.__parent(pos)
        while parent is not None and \
              self.cmp(self.key[self.__heap[parent]], self.key[item]) > 0:
            self.__heap[pos] = self.__heap[parent]
            self.__update_index(pos)
            pos, parent = parent, self.__parent(parent)
        self.__heap[pos] = item
        self.__update_index(pos)
    
    def __siftdown(self, item, pos = None):
        if pos is None:
            pos = self.__heap_index[item]
        child = self.__min_child(pos)
        while child is not None and \
              self.cmp(self.key[self.__heap[child]], self.key[item]) < 0:
            self.__heap[pos] = self.__heap[child]
            self.__update_index(pos)
            pos, child = child, self.__min_child(child)
        self.__heap[pos] = item
        self.__update_index(pos)
    
    def __delete(self, item, item_index = None):
        if item_index is None:
            item_index = self.__heap_index(item)
        swap_item = self.__heap.pop()
        del self.__heap_index[item]
        if item_index != len(self.__heap):
            if self.cmp(self.key[swap_item], self.key[item]) > 0:
                self.__siftdown(swap_item, item_index)
            else:
                self.__siftup(swap_item, item_index)
    
    def findmin(self):
        """
        Return an item from the heap with the minimum key value
        """
        return None if not self.__heap else self.__heap[0]
    
    def findminkey(self):
        """
        Return the minimum key value from the heap
        """
        return None if not self.__heap else self.key[self.__heap[0]]
    
    def insert(self, item, key = None):
        """
        Add an item to the heap. If the key is not provided, the
        key is taken from the heap's internal key map. If, in
        addition, the key is not available in the heap's internal
        key map, the key is taken to be the item itself.
        """
        if key is not None:
            self.key[item] = key
        elif item not in self.key:
            self.key[item] = item
        self.__heap.append(None)
        self.__siftup(item, len(self.__heap) - 1)

    def deletemin(self):
        """
        Remove an item with minimum key from the heap and return it.
        """
        item = self.findmin()
        if item is None:
            raise IndexError, 'delete from empty heap'
        self.__delete(item, 0)
        return item
    
    def meld(self, heap):
        """
        Add all of the items from the given heap into this heap.
        If the given heap has identical items to this heap that
        map to different keys, the mappings from the given heap
        take precedence.
        """
        self.__heap.extend(heap)
        self.key.update(heap.key)
        self.__heapify()
        
    def modifykey(self, item, new_key):
        """
        Change the key associated with the given item.
        """
        old_key, self.key[item] = self.key[item], new_key
        if self.cmp(new_key, old_key) < 0:
            self.__siftup(item)
        elif self.cmp(new_key, old_key) > 0:
            self.__siftdown(item)
        
    def getkey(self, item):
        """
        Return the key that the heap has associated with the given item
        """
        return self.key.get(item)

    def __contains__(self, item):
        return self.__heap_index.get(item) is not None

