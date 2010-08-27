import py.test

from yaupon.tests.testutils import pytest_generate_tests
from yaupon.data_structures.pairing_heaps import PairingHeap

def test_construction(backend):
    h = PairingHeap(backend=backend)
    assert h.findmin() is None
    with py.test.raises(StandardError):
        h.deletemin()

    h = PairingHeap(backend=backend, items=xrange(5))
    assert h.findmin() == 0
    for x in xrange(5):
        assert h.getkey(x) == x
    for x in xrange(5):
        assert h.deletemin() == x

    alphabet = 'abcdefghij'
    h = PairingHeap(backend=backend, 
                    keys=dict(zip(alphabet, xrange(len(alphabet)))))
    assert h.findmin() == 'a'
    for x in alphabet:
        assert h.getkey(x) == ord(x) - ord('a')
    for x in alphabet:
        assert h.deletemin() == x

def test_interleaved_insertions(backend):
    h = PairingHeap(backend=backend)
    def assertmin(x):
        assert h.findmin() == x
        assert h.deletemin() == x

    h.insert('a', 20)
    assertmin('a')
    h.insert('a', 10)
    assertmin('a')
    h.insert('a', 10)
    h.insert('b', 5)
    assertmin('b')
    assertmin('a')
    h.insert('a', 10)
    h.insert('b', 5)
    h.insert('c', 7)
    h.insert('d', 12)
    h.insert('e', 1)
    h.insert('f', 11)
    h.insert('g', 2)
    assertmin('e')
    assertmin('g')
    assertmin('b')
    assertmin('c')
    assertmin('a')
    assertmin('f')
    assertmin('d')

