import sqlite3

import yaupon.backend
from yaupon.data_structures.sqlite_tools import to_db, from_db


class SQLiteDictIterator(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self): 
        return self

    def next(self):
        result = self.cursor.fetchone()
        if result is None:
            raise StopIteration
        else:
            return self.transform(result)

class SQLiteDictScalarIterator(SQLiteDictIterator):
    def __init__(self, cursor):
        SQLiteDictIterator.__init__(self, cursor)
    
    def transform(self, result):
        return from_db(result[0])

class SQLiteDictRowIterator(SQLiteDictIterator):
    def __init__(self, cursor):
        SQLiteDictIterator.__init__(self, cursor)
    
    def transform(self, result):
        return tuple(map(from_db, result))

class SQLiteDict(object):
    def __init__(self, 
                 backend=None,
                 id=None,
                 pickle_protocol=2,
                 dict_args=None,
                 dict_kwargs=None):
        if backend is None:
            backend = yaupon.backend.BackendSQLite()
        self.backend = yaupon.backend.getbackend(backend)
        self.conn = backend.conn
        self.pickle_protocol = pickle_protocol
        self.conn.execute("""CREATE TABLE IF NOT EXISTS dict_instances
                             (id INTEGER PRIMARY KEY AUTOINCREMENT)
                          """)
        if id is not None:
            self.id = id
        else:
            self.id = self.conn.execute("""INSERT INTO dict_instances 
                                           VALUES (NULL)""").lastrowid

        self.conn.execute("""CREATE TABLE IF NOT EXISTS dict_%s
                             (key BLOB UNIQUE,
                              value BLOB)
                          """ % self.id)
        self.conn.execute("""CREATE INDEX IF NOT EXISTS dict_%s_key_index
                             ON dict_%s(key)
                          """ % (self.id, self.id))
        self.conn.commit()

        self.__get_STMT = 'SELECT value FROM dict_%s WHERE key = ?' % \
                          self.id
        self.__set_STMT = """REPLACE INTO dict_%s (key, value) 
                             VALUES (?,?)""" % self.id
        self.__delete_STMT = 'DELETE FROM dict_%s WHERE key = ?' % self.id

        if dict_args is None:
            dict_args = []
        if dict_kwargs is None:
            dict_kwargs = {}
        initial_dict = dict(*dict_args, **dict_kwargs)
        self.update(initial_dict)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['backend']
        del state['conn']
        state['backend_id'] = self.backend.id
        return state

    def __setstate__(self, state):
        backend_id = state.pop('backend_id')
        self.__dict__.update(state)
        self.backend = yaupon.backend.get_cached_sqlite_backend(backend_id)
        self.conn = self.backend.conn

    def __backend__(self):
        return self.backend

    def __get_helper(self, key):
        cursor = self.conn.execute(self.__get_STMT, (to_db(key),))
        return cursor.fetchone()

    def __getitem__(self, key):
        result = self.__get_helper(key)
        if result is None:
            raise KeyError(key)
        return from_db(result[0])

    def __setitem__(self, key, value):
        self.conn.execute(self.__set_STMT, (to_db(key), to_db(value)))
        self.conn.commit()

    def __delitem__(self, key):
        result = self.__get_helper(key)
        if result is None:
            raise KeyError(key)
        self.conn.execute(self.__delete_STMT, (to_db(key),))
        self.conn.commit()

    def has_key(self, key):
        return self.__get_helper(key) is not None

    def __contains__(self, key):
        return self.has_key(key)

    def get(self, key, defaultval=None):
        result = self.__get_helper(key)
        if result is None:
            return defaultval
        return from_db(result[0])

    def clear(self):
        self.conn.execute('DELETE FROM dict_%s' % self.id)
        self.conn.commit()

    def update(self, d):
        for k,v in d.iteritems():
            self.__setitem__(k,v)

    def setdefault(self, key, value=None):
        real_value = self.__get_helper(key)
        if real_value is None:
            self.__setitem__(key, value)
            return value
        else:
            return from_db(real_value[0])

    def iteritems(self):
        cursor = self.conn.execute("""SELECT key,value
                                      FROM dict_%s""" % self.id)
        return SQLiteDictRowIterator(cursor)

    def iterkeys(self):
        cursor = self.conn.execute('SELECT key FROM dict_%s' % self.id)
        return SQLiteDictScalarIterator(cursor)

    def itervalues(self):
        cursor = self.conn.execute('SELECT value FROM dict_%s' % self.id)
        return SQLiteDictScalarIterator(cursor)

    def __len__(self):
        cursor = self.conn.execute('SELECT COUNT(*) FROM dict_%s' % self.id)
        return cursor.fetchone()[0]
