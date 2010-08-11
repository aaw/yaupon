import cPickle as pickle
import sqlite3
import uuid

import yaupon.backend
from yaupon.data_structures.sqlite_tools import to_db, from_db
import edge
import exceptions
import id_generators

#TODO: add version info to the file format
#TODO: remove SQLiteProperty class, replace with SQLiteDict sharing backend
class SQLiteGraph(object):
    def __init__(self, 
                 vertices=None,
                 edges=None,
                 backend=None,
                 use_vertex_cache = False):
        self.__properties = {}
        if backend is None:
            backend = yaupon.backend.BackendSQLite()
        self.backend = backend
        self.conn = self.backend.conn
#        self.conn.text_factory = str
        self.__set_up_database__()

        #TODO: make EdgeType a property, have to ensure that it's
        #      multi-edge compatible?
        #TODO: pickle these properties in a separate table
        self.EdgeType = edge.MultiEdge
        self.GenerateVertexName = id_generators.UUIDGenerator()
        self.PythonTypeToDBType = to_db
        self.DBTypeToPythonType = from_db

        # Initialize vertex cache
        # TODO: make this a property so it can be turned on and off
        if use_vertex_cache:
            self.__vertex_cache = {}
            cursor = self.conn.execute('SELECT vertex, id from Vertices')
            result = cursor.fetchone()
            while result is not None:
                vertex_name = self.DBTypeToPythonType(result[0])
                self.__vertex_cache[vertex_name] = result[1] 
                result = cursor.fetchone()
        else:
            self.__vertex_cache = None

        # Initialize properties
        cursor = self.conn.execute("""SELECT tbl_name, python_name 
                                      FROM Properties""")
        for result in cursor.fetchall():
            prop = SQLiteProperty(self, result[0])
            setattr(self, result[1], prop)
            self.__properties[result[1]] = prop

        if vertices is not None:
            for v in vertices:
                self.add_vertex(v)
        if edges is not None:
            for x,y in edges:
                self.add_edge(self.add_vertex(x), self.add_vertex(y))

    def __backend__(self):
        return yaupon.backend.BackendSQLite()

    def __getattr__(self, name):
        prop = self.__properties.get(name)
        if prop is None:
            raise AttributeError
        return prop

    def create_edge_indexes(self):
        self.conn.execute("""
                          CREATE INDEX IF NOT EXISTS Edges_index_source
                          ON Edges (source)
                          """)

        self.conn.execute("""
                          CREATE INDEX IF NOT EXISTS Edges_index_target
                          ON Edges (target)
                          """)

    def drop_edge_indexes(self):
        self.conn.execute('DROP INDEX IF EXISTS Edges_index_source')
        self.conn.execute('DROP INDEX IF EXISTS Edges_index_source')
        self.conn.execute('VACUUM')

    def vertices(self):
        if self.__vertex_cache is not None:
            for v in self.__vertex_cache.iterkeys():
                yield v
        else:
            cursor = self.conn.execute('select vertex from Vertices')
            result = cursor.fetchone()
            while result is not None:
                yield self.DBTypeToPythonType(result[0])
                result = cursor.fetchone()

    def edges(self, source = None, target = None):
        query = """select e.id, s.vertex, t.vertex 
                   from Edges e, Vertices s, Vertices t
                   where e.source = s.id
                     and e.target = t.id"""
        if source is not None:
            query += " and e.source = %s " % self.vertex_to_db_id(source)
        if target is not None:
            query += " and e.target = %s " % self.vertex_to_db_id(target)
        cursor = self.conn.execute(query)
        result = cursor.fetchone()
        while result is not None:
            yield self.EdgeType(id = result[0],
                                source = self.DBTypeToPythonType(result[1]),
                                target = self.DBTypeToPythonType(result[2]))
            result = cursor.fetchone()

    def add_edge(self, source, target):
        edge = self.EdgeType(source, target)
        self.__add_edge_in_db(edge)
        return edge

    def add_vertex(self, v = None):
        definitely_need_to_insert = False
        if v is None:
            v = self.GenerateVertexName()
            definitely_need_to_insert = True
        if not definitely_need_to_insert:
            try:
                self.vertex_to_db_id(v)
            except exceptions.VertexNotFoundError:
                definitely_need_to_insert = True
        if definitely_need_to_insert:
            insert_vertex_ddl = "insert into Vertices(vertex) values (?)"
            cursor = self.conn.execute(insert_vertex_ddl,
                                       (self.PythonTypeToDBType(v),))
            self.conn.commit()
            if self.__vertex_cache is not None:
                self.__vertex_cache[v] = cursor.lastrowid
        return v

    def remove_edge(self, edge):
        self.conn.execute("delete from Edges where id = ?", (edge.id,))
        self.conn.commit()

    def remove_vertex(self, vertex):
        vertex_id = self.vertex_to_db_id(vertex)
        self.conn.execute("""delete from Edges 
                             where source = ? or target = ?""",
                          (vertex_id, vertex_id))
        self.conn.execute("delete from Vertices where id = ?", (vertex_id,))
        self.conn.commit()
        if self.__vertex_cache is not None:
            del self.__vertex_cache[vertex]

    def add_property(self, name):
        property = SQLiteProperty(self)
        self.__properties[name] = property
        self.conn.execute("""INSERT INTO 
                             Properties(tbl_name, python_name) 
                             VALUES (?,?)
                          """, (property.table_name, name))
        self.conn.commit()

    def properties(self):
        return self.__properties

    def remove_property(self, name):
        del self.__properties[name]

    def vertex_to_db_id(self, vertex):
        if self.__vertex_cache is not None:
            id = self.__vertex_cache.get(vertex)
            if id is None:
                raise exceptions.VertexNotFoundError(vertex)
            return id
        
        vertex_query = "select id from Vertices where vertex = ?"
        cursor = self.conn.execute(vertex_query, 
                                   (self.PythonTypeToDBType(vertex),))
        result = cursor.fetchone()
        if result is None:
            raise exceptions.VertexNotFoundError(vertex)
        return result[0]

    def __db_id_to_vertex(self, id):
        vertex_query = "select vertex from Vertices where id = ?"
        cursor = self.conn.execute(vertex_query, (id,))
        result = cursor.fetchone()
        if result is None:
            raise exceptions.VertexNotFoundError(vertex)
        return self.DBTypeToPythonType(result[0])

    def __add_edge_in_db(self, edge):
        try:
            source = self.vertex_to_db_id(edge.source)
        except exceptions.VertexNotFoundError:
            source = self.vertex_to_db_id(self.add_vertex(edge.source))
        try:
            target = self.vertex_to_db_id(edge.target)
        except exceptions.VertexNotFoundError:
            target = self.vertex_to_db_id(self.add_vertex(edge.target))
        s = "insert into Edges(source, target) values (?,?)"
        cursor = self.conn.execute(s, (source, target))                       
        edge.id = cursor.lastrowid
        self.conn.commit()

    def __set_up_database__(self):
        self.conn.execute('PRAGMA count_changes=OFF;')

        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS Vertices
                          (id INTEGER PRIMARY KEY,
                           vertex BLOB)
                          """)
        
        self.conn.execute("""
                          CREATE INDEX IF NOT EXISTS Vertices_index_vertex
                          ON Vertices (vertex)
                          """)

        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS Edges
                          (id INTEGER PRIMARY KEY,
                           source INTEGER, 
                           target INTEGER)
                          """)

        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS Properties
                          (id INTEGER PRIMARY KEY,
                           tbl_name TEXT UNIQUE,
                           python_name TEXT UNIQUE)
                          """)


class SQLiteProperty(object):

    def __init__(self, graph, table_name = None):
        self.graph = graph
        if table_name is None:
            self.table_name = '__Property__%s' % \
                              str(uuid.uuid4()).replace('-','')
        else:
            self.table_name = table_name
        self.conn = self.graph.conn

        self.__getitem_q = \
            """               
            select property 
            from %s 
            where id = ?
            """ % self.table_name

        self.__setitem_exists_q = \
            """ 
            select property
            from %s
            where id = ?
            """ % self.table_name

        self.__setitem_insert_q = \
            """
            insert into %s(id,property) values (?,?)
            """ % self.table_name

        self.__setitem_update_q = \
            """
            update %s
            set property = ?
            where id = ?
            """ % self.table_name

        self.__delitem_q = \
            """
            delete from %s
            where id = ?
            """ % self.table_name

        self.__drop_table_ddl = 'drop table %s' % self.table_name

        self.__delete_property_entry_ddl = \
            """
            delete Properties where tbl_name = '%s'
            """ % self.table_name

        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS %s
                          (id INTEGER PRIMARY KEY,
                           property BLOB)
                          """ % self.table_name)
    
    def id(self, obj):
        if type(obj) == self.graph.EdgeType:
            return obj.id
        else:
            return self.graph.vertex_to_db_id(obj)

    def __del__(self):
        self.conn.execute(self.__drop_table_ddl)
        self.conn.execute(self.__delete_property_ddl)
        self.conn.commit()

    def __getitem_helper(self, key):
        cursor = self.conn.execute(self.__getitem_q, (self.id(key),))
        return cursor.fetchone()        

    def get(self, key):
        result = self.__getitem_helper(key)
        if result is not None:
            return self.graph.DBTypeToPythonType(result[0])
        return None

    def __getitem__(self, key):
        result = self.__getitem_helper(key)
        if result is None:
            raise KeyError, key
        return self.graph.DBTypeToPythonType(result[0])

    def __setitem__(self, key, value):
        key_id = self.id(key)
        cursor = self.conn.execute(self.__setitem_exists_q, (key_id,))
        if cursor.fetchone() is None:
            self.conn.execute(self.__setitem_insert_q,
                              (key_id, self.graph.PythonTypeToDBType(value)))
        else:
            self.conn.execute(self.__setitem_update_q,
                              (self.graph.PythonTypeToDBType(value), key_id)) 
        self.conn.commit()

    def __delitem__(self, key):
        self.conn.execute(self.__delitem_q, (self.id(key),))
        self.conn.commit()

