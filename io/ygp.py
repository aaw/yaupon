import cPickle as pickle

pickle_protocol = 2

YGP_MAX_PROTOCOL = 0

class ProtocolError(StandardError): pass

def load(f, g):
    properties = []
    
    protocol = pickle.load(f)
    if protocol > YGP_MAX_PROTOCOL:
        raise ProtocolError, 'Unknown ygp protocol version: %s' % protocol

    s = pickle.load(f)
    while s is not None:
        g.add_property(s)
        properties.append(s)
        s = pickle.load(f)
        
    v = pickle.load(f)
    while v is not None:
        g.add_vertex(v)
        for property in properties:
            property_val = pickle.load(f)
            if property_val is not None:
                g.properties()[property][v] = property_val
        v = pickle.load(f)        

    while True:
        try:
            u = pickle.load(f)
        except EOFError: 
            break
        v = pickle.load(f)
        e = g.add_edge(u,v)
        for property in properties:
            property_val = pickle.load(f)
            if property_val is not None:
                g.properties()[property][e] = property_val
    return g


def dump(f, g, protocol = YGP_MAX_PROTOCOL):
    properties = []

    pickle.dump(protocol, f, pickle_protocol)

    for property_name in g.properties().keys():
        pickle.dump(property_name, f, pickle_protocol)
        properties.append(property_name)

    pickle.dump(None, f, pickle_protocol)
    for v in g.vertices():
        pickle.dump(v, f, pickle_protocol)
        for property in properties:
            pickle.dump(g.properties()[property].get(v), f, pickle_protocol)

    pickle.dump(None, f, pickle_protocol)
    for e in g.edges():
        pickle.dump(e[0], f, pickle_protocol)
        pickle.dump(e[1], f, pickle_protocol)
        for property in properties:
            pickle.dump(g.properties()[property].get(e), f, pickle_protocol)

if __name__ == '__main__':
    import sys
    import os
    import yaupon
    if len(sys.argv) < 2:
        print 'Usage: blah blah'
    elif len(sys.argv) < 3:
        f = open(sys.argv[1], 'rb')
        g = yaupon.Graph()
        load(f,g)
        print 'Vertices: %s' % ', '.join(str(v) for v in g.vertices())
        print 'Edges: %s' % ', '.join(str(e) for e in g.edges())
        print 'Properties:'
        for prop_name, prop in g.properties().items():
            print '%s: {%s}' % \
                (prop_name, str([(x,y) for x,y in prop.items()]))
        f.close()
    elif len(sys.argv) < 4:
        g = yaupon.Graph()
        try:
            f = open(sys.argv[1], 'rb')
            print 'Executing "%s" on %s' % (sys.argv[2], sys.argv[1])
            load(f,g)
        except:
            print "Couldn't load graph, overwriting"
    
        exec(sys.argv[2])
        f = open(sys.argv[1], 'wb')
        dump(f,g)
        f.close()
