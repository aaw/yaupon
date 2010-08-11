import cPickle as pickle
import sqlite3

import yaupon.backend
from yaupon.data_structures.sqlite_tools import to_db, from_db

class SQLiteDequeIterator(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def next(self):
        result = self.cursor.fetchone()
        if result is None:
            raise StopIteration
        else:
            return from_db(result[0])

class SQLiteDeque(object):
    def __init__(self, 
                 backend=None,
                 id = None,
                 pickle_protocol = 2):
        if backend is None:
            backend = yaupon.backend.BackendSQLite()
        self.backend = yaupon.backend.getbackend(backend)
        self.conn = backend.conn
        self.pickle_protocol = pickle_protocol
        self.conn.execute("""CREATE TABLE IF NOT EXISTS deque_instances
                             (id INTEGER PRIMARY KEY AUTOINCREMENT)
                          """)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS deque_fingers
                             (id INTEGER PRIMARY KEY,
                              front INTEGER,
                              back INTEGER)
                          """)
        if id is not None:
            self.id = id
        else:
            self.id = self.conn.execute("""INSERT INTO deque_instances 
                                           VALUES (NULL)""").lastrowid
            self.conn.execute("""INSERT INTO deque_fingers
                                 VALUES (?,0,0)""", (self.id,))
            self.conn.commit()
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS deque_%s
                             (id INTEGER PRIMARY KEY,
                              value BLOB)
                          """ % self.id)
        self.__get_element_from_back = """SELECT value 
                                          FROM deque_%s d, deque_fingers f 
                                          WHERE f.id = %s
                                            AND d.id = f.back + ?""" % \
                                          (self.id, self.id)
        self.__get_element_from_front = """SELECT value 
                                           FROM deque_%s d, deque_fingers f 
                                           WHERE f.id = %s
                                             AND d.id = f.front + ?""" % \
                                           (self.id, self.id)
        self.__set_element_from_back = """REPLACE INTO deque_%s 
                                          (id, value) 
                                          SELECT f.back + ?, ?
                                          FROM deque_fingers f
                                          WHERE f.id = %s""" % \
                                          (self.id, self.id)
        self.__set_element_from_front = """REPLACE INTO deque_%s 
                                           (id, value) 
                                           SELECT f.front + ?, ?
                                           FROM deque_fingers f
                                           WHERE f.id = %s""" % \
                                           (self.id, self.id)

    def __backend__(self):
        return self.backend

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

    def __getitem__(self, index):
        if index < 0:
            sql = self.__get_element_from_back
        else:
            sql = self.__get_element_from_front
        cursor = self.conn.execute(sql, (index,))
        result = cursor.fetchone()
        if result is None:
            raise IndexError, index
        return from_db(result[0])

    def __setitem__(self, index, value):
        if index < 0:
            sql = self.__set_element_from_back
        else:
            sql = self.__set_element_from_front
        cursor = self.conn.execute(sql, 
                                   (index, to_db(value, self.pickle_protocol)))

    def __iter__(self):
        cursor = self.conn.execute("""SELECT d.value 
                                      FROM deque_%s d, deque_fingers f
                                      WHERE d.id >= f.front
                                        AND d.id < f.back
                                        AND f.id = ?""" % self.id, (self.id,))
        return SQLiteDequeIterator(cursor)

    def __increment_front_finger(self):
        self.conn.execute("""UPDATE deque_fingers
                             SET front = front + 1
                             WHERE id = ?""", (self.id,))

    def __decrement_front_finger(self):
        self.conn.execute("""UPDATE deque_fingers
                             SET front = front - 1
                             WHERE id = ?""", (self.id,))

    def __increment_back_finger(self):
        self.conn.execute("""UPDATE deque_fingers
                             SET back = back + 1
                             WHERE id = ?""", (self.id,))

    def __decrement_back_finger(self):
        self.conn.execute("""UPDATE deque_fingers
                             SET back = back - 1
                             WHERE id = ?""", (self.id,))

    def __back_finger(self):
        cursor = self.conn.execute("""SELECT back 
                                      FROM deque_fingers
                                      WHERE id = ?""", (self.id,))
        return cursor.fetchone()[0]

    def __front_finger(self):
        cursor = self.conn.execute("""SELECT front 
                                      FROM deque_fingers
                                      WHERE id = ?""", (self.id,))
        return cursor.fetchone()[0]

    def __len__(self):
        cursor = self.conn.execute("""SELECT back - front
                                      FROM deque_fingers
                                      WHERE id = ?""", (self.id,))
        return cursor.fetchone()[0]

    def __get_helper(self, sql, *args):
        cursor = self.conn.execute(sql, args)
        result = cursor.fetchone()
        if result is None:
            raise IndexError, index
        return from_db(result[0])

    def __set_helper(self, sql, *args):
        cursor = self.conn.execute(sql, args)

    def pop(self):
        self.__decrement_back_finger()
        self.conn.commit()
        return self.__get_helper(self.__get_element_from_back, 0)

    def append(self, value):
        self.__set_helper(self.__set_element_from_back, 
                          0, to_db(value, self.pickle_protocol))
        self.__increment_back_finger()
        self.conn.commit()

    def popleft(self):
        val = self.__get_helper(self.__get_element_from_front, 0)
        self.__increment_front_finger()
        self.conn.commit()
        return val
    
    def appendleft(self, value):
        self.__decrement_front_finger()
        self.__set_helper(self.__set_element_from_front, 
                          0, to_db(value, self.pickle_protocol))
        self.conn.commit()

    def extend(self, l):
        for item in l:
            self.append(item)
