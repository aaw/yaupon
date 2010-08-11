import collections
import sqlite3
import uuid

#backend protocol is:
# class can implement __backend__, which returns a storage class
# if no __backend__ implemented, core memory is used for storage.
# Backend* classes return self from __backend__
#
# want the following things to happen:
# g1 = yaupon.Graph() # core
# g2 = yaupon.Graph(backend=BackendCore()) # still core
# g3 = yaupon.Graph(BackendSQLite()) #temp sqlite file
# g4 = yaupon.Graph(BackendSQLite('my_backend.db')) # named sqlite file
# 
# d = ydict(backend=backend(g1)) # d is a dict()
# d = ydict(backend=BackendCore(), source=d_prime) # source is passed to
#                                                  # dict constructor
# d = ydict(backend=backend(g3)) # d inherits g3's tempfile backend, or
#                                # whatever backend g returns

def getbackend(obj):
    try:
        return obj.__backend__()
    except AttributeError:
        return BackendCore()

class BackendCore(object):
    def __backend__(self):
        return self

    def create_deque(self, *args, **kwargs):
        return collections.deque(*args, **kwargs)

    def create_dict(self, *args, **kwargs):
        return dict(*args, **kwargs)

    def sorted(self, *args, **kwargs):
        return iter(sorted(*args, **kwargs))

class BackendSQLite(object):
    def __init__(self, conn=None, id=None):
        if id is None:
            self.id = str(uuid.uuid4())
            if conn is None:
                conn = sqlite3.connect('') #temp file
            self.conn = conn
            sqlite_connection_cache[self.id] = self.conn
            self.backend_owner = True
        else:
            self.id = id
            self.conn = sqlite_connection_cache[id]
            self.backend_owner = False

    def __del__(self):
        if self.backend_owner and self.id in sqlite_connection_cache:
            del sqlite_connection_cache[self.id]

    def __backend__(self):
        return self

    def create_deque(self, *args, **kwargs):
        from yaupon.data_structures.sqlite_deque import SQLiteDeque
        return SQLiteDeque(backend=self, *args, **kwargs)

    def create_dict(self, *args, **kwargs):
        from yaupon.data_structures.sqlite_dict import SQLiteDict
        return SQLiteDict(backend=self, *args, **kwargs)

    def sorted(self, *args, **kwargs):
        from yaupon.data_structures.dheap import DHeap
        if 'key' in kwargs:
            heap = DHeap(backend=self, items=args[0], key=kwargs['key'])
        else:
            heap = DHeap(backend=self, items=args[0])
        while heap:
            yield heap.deletemin()

# sqlite_backend_cache : backend_id -> connection
sqlite_connection_cache = {}

def get_cached_sqlite_backend(id):
    return BackendSQLite(id=id)
