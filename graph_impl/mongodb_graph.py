import re

import pymongo
from pymongo.objectid import ObjectId

import edge
import exceptions


class MongoDBGraph(object):
    def __init__(self, db, namespace, vertices = None, edges = None):
        self.db = db
        self.namespace = namespace
        self.vertex_collection().ensure_index('name')
        self.edge_collection().ensure_index('source')
        self.edge_collection().ensure_index('target')
        self.EdgeType = edge.MultiEdge
        self.GenerateVertexName = ObjectId
        if vertices is not None:
            for v in vertices:
                self.add_vertex(v)
        if edges is not None:
            for x,y in edges:
                self.add_edge(self.add_vertex(x), self.add_vertex(y))

    def vertex_collection(self):
        return self.db['%s.%s' % (self.namespace, 'vertices')]

    def edge_collection(self):
        return self.db['%s.%s' % (self.namespace, 'edges')]

    def __getattr__(self, name):
        return MongoProperty(self, self.db, self.namespace, name)

    def vertices(self):
        for doc in self.vertex_collection().find({},{'name':1}):
            yield doc['name']

    def edges(self, source = None, target = None):
        conditions = {}
        conditions['source'] = source
        conditions['target'] = target
        for edge in self.edge_collection().find(conditions,{'source':1, 'target':1}):
            yield self.EdgeType(source=edge['source'], target=edge['target'], id=edge['_id'])

    def add_edge(self, source, target):
        self.add_vertex(source)
        self.add_vertex(target)
        object_id = self.edge_collection().insert({'source': source, 'target': target})
        return self.EdgeType(source=source, target=target, id=object_id)

    def add_vertex(self, v = None):
        if v is None:
            v = self.GenerateVertexName()
        self.vertex_collection().update({'name': v}, {'name': v}, upsert=True)
        return v

    def remove_edge(self, edge):
        self.edge_collection().remove({'_id': edge.id})

    def remove_vertex(self, vertex):
        if self.vertex_collection().find_one({'name': vertex},{'name':1}) is None:
            raise exceptions.VertexNotFoundError(vertex)
        self.edge_collection().remove({'source': vertex})
        self.edge_collection().remove({'target': vertex})
        self.vertex_collection().remove({'name': vertex})

    def add_property(self, name):
        pass
    
    def remove_property(self, name):
        self.db['%s.%s.%s' % (self.namespace, 'property', name)].drop()

    def properties(self):
        properties_re = re.compile('%s\\.property\\.(.*)' % self.namespace)
        for collection_name in self.db.collection_names:
            match = properties_re.match(collection_name)
            if match is not None:
                yield match.groups()[0]

class MongoProperty(object):
    def __init__(self, graph, db, namespace, property_name):
        self.graph = graph
        self.coll = db['%s.%s.%s' % (namespace, 'property', property_name)]
        self.coll.ensure_index('document_id')

    def get_id(self, item):
        if type(item) == self.graph.EdgeType:
            return item.id
        else:
            return self.graph.vertex_collection().find_one({'name': item})['_id']

    def __getitem__(self, item):
        value = self.coll.find_one({'document_id': self.get_id(item)}, {'value':1})
        if value is None:
            return None
        return value['value']

    def __setitem__(self, item, value):
        self.coll.update({'document_id': self.get_id(item)}, {'$set': {'value': value}}, upsert=True)

