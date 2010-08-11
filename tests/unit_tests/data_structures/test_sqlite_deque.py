from yaupon.backend import BackendSQLite
import yaupon.data_structures.sqlite_deque as deque
from yaupon.tests.testutils import TempFile

def test_back_modifications():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    q.append(1)
    q.append(2)
    q.append(3)
    q.append(4)
    assert q.pop() == 4
    assert q.pop() == 3
    assert q.pop() == 2
    assert q.pop() == 1

def test_front_modifications():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    q.appendleft(1)
    q.appendleft(2)
    q.appendleft(3)
    q.appendleft(4)
    assert q.popleft() == 4
    assert q.popleft() == 3
    assert q.popleft() == 2
    assert q.popleft() == 1

def test_mixed_modifications():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    # []
    q.appendleft('y') 
    # [y]
    q.appendleft('b') 
    # [by]
    assert q.popleft() == 'b' 
    # [y]
    q.appendleft('x') 
    # [xy]
    assert q.popleft() == 'x' 
    # [y]
    q.appendleft('a') 
    # [ay]
    q.appendleft('z')
    # [zay]
    q.append('c')
    # [zayc]
    assert q.pop() == 'c'
    # [zay]
    assert q.popleft() == 'z'
    # [ay]
    assert q.popleft() == 'a'
    # [y]
    assert q.pop() == 'y'
    # []
    q.appendleft('m')
    # [m]
    assert q.pop() == 'm'
    # []
    q.append('n')
    # [n]
    assert q.popleft() == 'n'
    # []

def test_insert_python_datatypes():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    q.append(1)
    q.append('a')
    q.append(12.342)
    q.append(None)
    q.append([1,2,3])
    q.append({1:'a',2:1.2})
    assert q.popleft() == 1
    assert q.popleft() == 'a'
    assert q.popleft() == 12.342
    assert q.popleft() is None
    l = q.popleft()
    assert l[0] == 1
    assert l[1] == 2
    assert l[2] == 3
    d = q.popleft()
    assert d[1] == 'a' 
    assert d[2] == 1.2

def test_getindex():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    q.append(4)
    q.appendleft(3)
    q.append(5)
    q.appendleft(2)
    q.append(6)
    q.appendleft(1)
    q.append(7)
    q.appendleft(0)

    def subtest(x):
        for i in xrange(x):
            assert q[i] == i
        for i in xrange(1,x):
            assert q[-i] == x-i

    for j in xrange(7):
        subtest(8-j)
        q.pop()

def test_iter_and_len():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    l = []
    for i in xrange(100):
        assert len(q) == len(l)
        q.append(i)
        l.append(i)

    for i in xrange(49):
        q.popleft()
        l.pop(0)
        assert len(q) == len(l)
        for x,y in zip(q,l):
            assert x == y
    
        q.pop()
        l.pop()
        assert len(q) == len(l)
        for x,y in zip(q,l):
            assert x == y

def test_multiple_deques_same_backend():
    backend = BackendSQLite()
    q1 = deque.SQLiteDeque(backend=backend)
    q2 = deque.SQLiteDeque(backend=backend)
    q3 = deque.SQLiteDeque(backend=backend)
    q1.append('hello')
    q1.appendleft('world')
    q2.appendleft('hello')
    q2.append('world')
    q3.append('foo')
    q3.append('bar')
    assert q1[0] == 'world'
    assert q1[1] == 'hello'
    assert q2[0] == 'hello'
    assert q2[1] == 'world'
    assert q3[0] == 'foo'
    assert q3[1] == 'bar'
    
def test_reboot_deque_from_backend():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    q.append('a')
    q.append('b')
    q.append('c')
    assert [x for x in q] == ['a','b','c']
    q2 = deque.SQLiteDeque(backend=backend, id=q.id)
    assert [x for x in q2] == ['a','b','c']
    q.popleft()
    q.append('d')
    q.appendleft('A')
    q.appendleft('Z')
    q.appendleft('Y')
    q2 = deque.SQLiteDeque(backend=backend, id=q.id)
    assert [x for x in q2] == ['Y','Z','A','b','c','d']

def test_multiple_instances_same_deque():
    backend = BackendSQLite()
    q = deque.SQLiteDeque(backend=backend)
    q2 = deque.SQLiteDeque(backend=backend, id=q.id)
    q.append(1)
    q2.append(2)
    q.append(3)
    q2.append(4)
    assert [x for x in q] == [x for x in q2]
    q.popleft()
    assert [x for x in q] == [x for x in q2]
    q2.pop()
    assert [x for x in q] == [x for x in q2]
    q.popleft()
    assert [x for x in q] == [x for x in q2]
    q2.pop()
    assert [x for x in q] == [x for x in q2]
