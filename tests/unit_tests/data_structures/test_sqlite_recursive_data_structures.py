from yaupon.backend import BackendSQLite
import yaupon.data_structures.sqlite_dict as sqlite_dict
import yaupon.data_structures.sqlite_deque as sqlite_deque
import yaupon.data_structures.sqlite_tools as sqlite_tools

def test_embedded_dicts():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    inner_d = sqlite_dict.SQLiteDict(backend=d)
    d['a'] = 1
    d['hello'] = inner_d
    inner_d['world'] = 'success!'
    inner_d['b'] = 'c'
    assert d['a'] == 1
    assert d['hello']['world'] == 'success!'
    assert d['hello']['b'] == 'c'
    inner_inner_dict = sqlite_dict.SQLiteDict(backend=inner_d)
    inner_inner_dict['success!'] = 'yes!'
    inner_d['world'] = inner_inner_dict
    assert d['hello']['world']['success!'] == 'yes!'

def test_multiple_references_same_dict():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    inner_d = sqlite_dict.SQLiteDict(backend=d)
    inner_d['key'] = 'value'
    d['a'] = inner_d
    d['b'] = inner_d
    d['c'] = inner_d
    assert d['a']['key'] == 'value'
    assert d['b']['key'] == 'value'
    assert d['c']['key'] == 'value'

def test_parent_dict_dies_before_child():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    inner_d = sqlite_dict.SQLiteDict(backend=d)
    d['hello'] = inner_d
    d['hello']['world'] = 'foobar'
    d = None
    assert inner_d['world'] == 'foobar'

def test_deque_inside_dict():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    q = sqlite_deque.SQLiteDeque(backend=d)
    d['a'] = q
    q.append(1)
    q.append(2)
    q.append(3)
    assert d['a'][0] == 1
    assert d['a'][1] == 2
    assert d['a'][-1] == 3
    assert d['a'].pop() == 3

def test_dict_inside_deque():
    backend = BackendSQLite()
    q = sqlite_deque.SQLiteDeque(backend=backend)
    q.append(sqlite_dict.SQLiteDict(backend=q))
    q.append(sqlite_dict.SQLiteDict(backend=q))
    q.append(sqlite_dict.SQLiteDict(backend=q))
    q[0]['hello'] = 'world'
    q[1]['hello'] = 'WORLD'
    q[-1]['hello'] = 'WORLD!!!'
    assert q.popleft()['hello'] == 'world'
    assert q.popleft()['hello'] == 'WORLD'
    assert q.popleft()['hello'] == 'WORLD!!!'
