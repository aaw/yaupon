import os
import functools
import sqlite3

import yaupon
import yaupon.backend as backend
import yaupon.graph_impl.dictgraph as dictgraph
import yaupon.graph_impl.sqlitegraph as sqlitegraph
import yaupon.graph_impl.forest as forest
import yaupon.graph_impl.exceptions as exceptions
import yaupon.io.ygp

class TempFile(object):
    def __init__(self, dir = None, prefix = None):
        self.filename = os.tempnam(dir, prefix)
        self.handle = None

    def __del__(self):
        try:
            if self.handle is not None:
                self.handle.close()
            os.remove(self.filename)
        except:
            pass

    def open(self, options):
        self.handle = open(self.filename, options)
        return self.handle

    def close(self):
        self.handle.close()
        self.handle = None

"""
import this function in unit tests, then any unit tests that have the
arguments "graph" or "graph_type" will pull in either instances or classes
of all of yaupon's graph implementations.
"""
def pytest_generate_tests(metafunc):
    if "graph" in metafunc.funcargnames:
        dict_g = dictgraph.DictGraph()
        memory_conn = sqlite3.connect(':memory:')
        memory_backend = backend.BackendSQLite(memory_conn)
        tempfile_1 = backend.BackendSQLite()
        tempfile_2 = backend.BackendSQLite()
        sqlite_memory_g = sqlitegraph.SQLiteGraph(backend=memory_backend)
        sqlite_tempfile_g = sqlitegraph.SQLiteGraph(backend=tempfile_1)
        sqlite_tempfile_vcache_g \
            = sqlitegraph.SQLiteGraph(backend=tempfile_2,
                                      use_vertex_cache = True)
        metafunc.addcall(funcargs = { 'graph' : dict_g })
        metafunc.addcall(funcargs = { 'graph' : sqlite_memory_g })
        metafunc.addcall(funcargs = { 'graph' : sqlite_tempfile_g })
        metafunc.addcall(funcargs = { 'graph' : sqlite_tempfile_vcache_g })
    elif "forest" in metafunc.funcargnames:
        f = forest.Forest()
        metafunc.addcall(funcargs = { 'forest' : f })
    elif "graph_type" in metafunc.funcargnames:
        metafunc.addcall(funcargs = { 'graph_type' : dictgraph.DictGraph })
        metafunc.addcall(funcargs = { 'graph_type' : sqlitegraph.SQLiteGraph })
    elif "forest_type" in metafunc.funcargnames:
        metafunc.addcall(funcargs = { 'forest_type' : forest.Forest })
    elif "backend" in metafunc.funcargnames:
        metafunc.addcall(funcargs = { 'backend' : backend.BackendCore() })
        conn = sqlite3.connect('')
        metafunc.addcall(funcargs = 
                         { 'backend' : backend.BackendSQLite(conn=conn) })

"""
import this function in data driven tests and wrap it to iterate over
instances of graphs from a database. for example, given a graph database
under the folder /foo/bar, you'd implement the following function:

 def pytest_generate_tests(metafunc):
     graph_database_iteration(metafunc, '/foo/bar')

then, any tests that have the argument "graph" will actually be run on
all graphs in the database /foo/bar. this iteration is lazy about loading
the graphs so that we don't load them all up front; inside the test function
you have to call "g = graph()" to load the graph.
"""
def graph_database_iteration(metafunc, database = None):
    if database is None:
        database = base_test_directory()
    if "graph" in metafunc.funcargnames:
        graph_generators = [dictgraph.DictGraph,
                            sqlitegraph.SQLiteGraph,
                            functools.partial(sqlitegraph.SQLiteGraph,
                                              use_vertex_cache=True)
                            ]
        for filename in find_all_ygp_files(database):
            for graphtype in graph_generators:
                metafunc.addcall(funcargs = { 'graph' : 
                                              lazy_loader(filename, graphtype)
                                              })

class lazy_loader(object):
    def __init__(self, path, GraphType):
        self.path = path
        self.GraphType = GraphType

    def __call__(self):
        g = self.GraphType()
        yaupon.io.ygp.load(open(self.path, 'rb'), g)
        return g

def find_all_ygp_files(path):
    for file in os.listdir(path):
        fullname = os.path.join(path, file)
        if os.path.isfile(fullname) and file.endswith('.ygp'):
            yield fullname
        elif os.path.isdir(fullname):
            for x in find_all_ygp_files(fullname):
                yield x

def base_test_directory():
    yaupon_base = os.path.split(yaupon.__file__)[0]
    return os.path.join(yaupon_base, 'tests', 'test_graphs')
