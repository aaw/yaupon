import py.test
import yaupon.data_structures.sqlite_dict as sqlite_dict
from yaupon.backend import BackendSQLite

def test_simple_getitem_and_setitem():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['b'] = 2
    d['c'] = 3
    d['d'] = 4
    d['d'] = 5
    assert d['a'] == 1
    assert d['b'] == 2
    assert d['c'] == 3
    assert d['d'] == 5
    py.test.raises(KeyError, "d['e']")    
    py.test.raises(KeyError, "d[1]")

def test_del():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['b'] = 2
    assert d['a'] == 1
    assert d['b'] == 2
    del d['a']
    py.test.raises(KeyError, "d['a']")
    assert d['b'] == 2
    del d['b']
    py.test.raises(KeyError, "d['a']")
    py.test.raises(KeyError, "d['b']")
    py.test.raises(KeyError, "del d['a']")
    py.test.raises(KeyError, "del d['foo']")

def test_get():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['b'] = 2
    d['c'] = 3
    assert d.get('a') == 1
    assert d.get('b') == 2
    assert d.get('c') == 3
    assert d.get('a',100) == 1
    assert d.get('d') is None
    assert d.get('d',100) == 100
    d['d'] = 4
    assert d.get('d',100) == 4
    assert d.get('d') == 4

def test_has_key_and_contains():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['b'] = 2
    d['c'] = 3
    assert d.has_key('a')
    assert d.has_key('b')
    assert d.has_key('c')
    assert 'a' in d
    assert 'b' in d
    assert 'c' in d
    assert not d.has_key('d')
    assert not d.has_key('ab')
    assert not d.has_key(1)
    assert 'd' not in d
    assert 'ab' not in d
    assert 1 not in d

def test_clear_and_len():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    assert len(d) == 1
    d['b'] = 2
    assert len(d) == 2
    d['c'] = 3
    assert len(d) == 3
    d.clear()
    assert len(d) == 0
    py.test.raises(KeyError, "d['a']")
    py.test.raises(KeyError, "d['b']")
    py.test.raises(KeyError, "d['c']")
    d['a'] = 1
    assert len(d) == 1
    d.clear()
    assert len(d) == 0
    py.test.raises(KeyError, "d['a']")

def test_iter():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['b'] = 2
    d['c'] = 3
    d['d'] = 4
    assert sorted([x for x in d.iterkeys()]) == sorted(['a','b','c','d'])
    assert sorted([x for x in d.itervalues()]) == sorted([1,2,3,4])
    assert sorted([x for x in d.iteritems()]) == \
           sorted([('a',1), ('b',2), ('c',3), ('d',4)])

def test_update():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d2 = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['b'] = 2
    d['c'] = 3
    d['d'] = 4
    d2['b'] = 22
    d2['c'] = 33
    d2['d'] = 44
    d2['e'] = 55
    d.update(d2)
    assert sorted([x for x in d.iteritems()]) == \
           sorted([('a',1), ('b',22), ('c',33), ('d',44), ('e',55)])

def test_setdefault():
    backend = BackendSQLite()
    d = sqlite_dict.SQLiteDict(backend=backend)
    d['a'] = 1
    d['c'] = 3
    d['e'] = 5
    assert d.setdefault('a',0) == 1
    assert d.setdefault('b',2) == 2
    assert d.setdefault('c',-1) == 3
    assert d.setdefault('d',4) == 4
    assert d.setdefault('e',None) == 5
    assert d.setdefault('f') is None
    assert d['a'] == 1
    assert d['b'] == 2
    assert d['c'] == 3
    assert d['d'] == 4
    assert d['e'] == 5
    assert d['f'] is None
    
def test_multiple_dicts_same_backend():
    backend = BackendSQLite()
    d1 = sqlite_dict.SQLiteDict(backend=backend)
    d2 = sqlite_dict.SQLiteDict(backend=backend)
    d3 = sqlite_dict.SQLiteDict(backend=backend)
    d1['a'] = 1
    d2['a'] = 2
    d3['a'] = 3
    assert d1['a'] == 1
    assert d2['a'] == 2
    assert d3['a'] == 3
    d1['a'] = 4
    d2['a'] = 5
    d3['a'] = 6
    assert d1['a'] == 4
    assert d2['a'] == 5
    assert d3['a'] == 6
    del d1['a']
    assert d1.get('a') is None
    assert d2['a'] == 5
    assert d3['a'] == 6
    del d2['a']
    assert d1.get('a') is None
    assert d2.get('a') is None
    assert d3['a'] == 6
    del d3['a']
    assert d1.get('a') is None
    assert d2.get('a') is None
    assert d3.get('a') is None
    
def test_multiple_instances_same_dict():
    backend = BackendSQLite()
    d1 = sqlite_dict.SQLiteDict(backend=backend)
    d2 = sqlite_dict.SQLiteDict(backend=backend, id=d1.id)
    d1['a'] = 1
    d2['b'] = 2
    d1['c'] = 3
    d2['d'] = 4
    assert [x for x in d1.iteritems()] == [x for x in d2.iteritems()]
    d2['b'] = 22
    assert [x for x in d1.iteritems()] == [x for x in d2.iteritems()]
    del d1['c']
    assert [x for x in d1.iteritems()] == [x for x in d2.iteritems()]
    d2['c'] = 3
    assert [x for x in d1.iteritems()] == [x for x in d2.iteritems()]
