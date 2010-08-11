from yaupon.tests.testutils import pytest_generate_tests
from yaupon.data_structures.union_find import UnionFind

def test_first_find(backend):
    u = UnionFind(backend=backend)
    assert u.find('a') == 'a'
    assert u.find('a') == 'a'    
    assert u.find(1) == 1
    assert u.find(1) == 1
    assert u.find(12.2) == 12.2    
    assert u.find(12.2) == 12.2
        
def test_link(backend):
    u = UnionFind(backend=backend)
    assert u.link(0,1) in [0,1]
    assert u.link(0,1) is None
    assert u.link(2,3) in [2,3]
    assert u.link(2,3) is None
    assert u.link(3,4) in [2,3,4]
    assert u.link(3,4) is None
    assert u.link(2,4) is None
    assert u.link(2,3) is None
    assert u.link(0,2) in [0,1,2,3,4]
    for x in xrange(5):
        for y in xrange(5):
            assert u.link(x,y) is None
    
def test_find(backend):
    u = UnionFind(backend=backend)
    u.link(0,1)
    u.link(2,3)
    assert u.find(0) == u.find(1)
    assert u.find(2) == u.find(3)
    assert u.find(4) == 4
    assert u.find(0) != u.find(2)
    assert u.find(0) != u.find(4)
    assert u.find(2) != u.find(4)
    u.link(0,2)
    assert u.find(0) == u.find(1)
    assert u.find(1) == u.find(2)
    assert u.find(2) == u.find(3)
    assert u.find(3) != u.find(4)
    u.link(3,4)
    assert u.find(0) == u.find(1)
    assert u.find(1) == u.find(2)
    assert u.find(2) == u.find(3)
    assert u.find(3) == u.find(4)
