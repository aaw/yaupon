from yaupon.tests.testutils import pytest_generate_tests
from yaupon.data_structures.dheap import  DHeap

def test_default_construct(backend):
    heap = DHeap(backend)
    populate_heap(heap)
    remove_items_from_heap(heap)
    populate_heap(heap, order='REVERSE')
    remove_items_from_heap(heap)
        
def test_construct_with_different_d_values(backend):
    heap = DHeap(backend, d=2)
    populate_heap(heap)
    remove_items_from_heap(heap)
    heap = DHeap(d=3, backend=backend)
    populate_heap(heap)
    remove_items_from_heap(heap)
    heap = DHeap(d=4, backend=backend)
    populate_heap(heap)
    remove_items_from_heap(heap)
    heap = DHeap(d=5, backend=backend)
    populate_heap(heap)
    remove_items_from_heap(heap)
        
def test_construct_with_sequence(backend):
    heap = DHeap(backend, items = xrange(1000))
    remove_items_from_heap(heap)
    
def test_construct_with_key_map(backend):
    key = dict()
    items = [x for x in xrange(1000)]
    for x in items:
        key[x] = len(items) - x        
            
    heap = DHeap(backend)
    populate_heap(heap, items=items, key=key)
    remove_items_from_heap(heap, key=key)

    heap = DHeap(backend)
    populate_heap(heap, items=items, key=key, order='REVERSE')
    remove_items_from_heap(heap, key=key)

def test_multiple_identical_keys(backend):
    heap = DHeap(backend)
    items = [x for x in xrange(100)] * 5
    populate_heap(heap, items=items)
    remove_items_from_heap(heap)

    heap = DHeap(backend)
    items = [x for x in 'abcdefghijklmnopqrstuvwxy']
    key = dict(zip(items, [0,1,2,3,4] * 5))
    populate_heap(heap, items=items, key=key)

    preimages = dict()
    for i in xrange(5):
        preimages[i] = set(x for x,y in key.iteritems() if y == i)
        
    for i in xrange(len(heap)):
        item = heap.deletemin()
        assert item in preimages[i / 5]
        preimages[i / 5].remove(item)
            
def test_meld(backend):
    h1 = DHeap(backend, items = [x for x in xrange(0,300)])
    h2 = DHeap(backend, items = [x for x in xrange(300,500)])
    h3 = DHeap(backend, items = [x for x in xrange(500,700)])
    h4 = DHeap(backend, items = [x for x in xrange(700,1000)])
        
    h1.meld(h2)
    h3.meld(h4)
    h1.meld(h3)
    
    assert sorted(x for x in h1) == [x for x in xrange(0,1000)] 
    remove_items_from_heap(h1)

def test_modify_key(backend):
    heap = DHeap(backend)
    populate_heap(heap, order='REVERSE')
        
    for item in reversed([x for x in heap]):
        heap.modifykey(item, -1)
        assert heap.findminkey() == -1
        assert heap.deletemin() == item
    
def test_get_key(backend):
    heap = DHeap(backend)
    populate_heap(heap)
    for item in heap:
        assert heap.getkey(item) == item

def populate_heap(heap, items=None, order=None, key=None):
    if items is None:
        items = xrange(100)
        
    if order is None or order == 'FORWARD':
        gen_items = items
    elif order == 'REVERSE':
        gen_items = reversed(items)

    for item in gen_items:
        if key is None:
            heap.insert(item)
        else:
            heap.insert(item, key[item])

def remove_items_from_heap(heap, key=None):
    if key is None:
        sequence = sorted(x for x in heap)
    else:
        sequence = sorted((x for x in heap), key = lambda x : key[x])
            
    for item in sequence:
        key = heap.getkey(item)
        assert heap.findmin() == item
        assert heap.findminkey() == key
        assert heap.deletemin() == item

