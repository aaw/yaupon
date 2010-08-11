import sys
import xml.etree.ElementTree as ET

import yaupon

graphml_namespace = "http://graphml.graphdrawing.org/xmlns"
graphml_namespace_xsi = "http://www.w3.org/2001/XMLSchema-instance"
graphml_xsi_schema_location = "http://graphml.graphdrawing.org/xmlns " + \
                       "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"


def read_graphml(f = sys.stdin,
                 GraphType = yaupon.Graph,
                 convert_node_tag_to_node = lambda x : x
                 ):
    
    g = GraphType()
    
    tree = ET.parse(f)
    xml_root = tree.getroot()
    
    deserialize = \
        {'int'      : lambda x : int(x),
         'double'   : lambda x : float(x),
         'string'   : lambda x : x,
         'boolean'  : lambda x : True if x.lower() == 'true' else False
        }
    
    # Get Node and Edge property types
    edge_keys = list()
    vertex_keys = list()
    key_types = dict()
    key_names = dict()
    defaults = dict()
    
    for key in xml_root.findall('.//{%s}key' % graphml_namespace):
        key_name = key.attrib.get('attr.name')
        key_type = key.attrib.get('attr.type')
        id = key.attrib.get('id')
        key_domain = key.attrib.get('for')
        if key_domain == 'edge':
            edge_keys.append(key_name)
        else:
            vertex_keys.append(key_name)

        g.make_property(key_name)
        default = key.find('.//{%s}default' % graphml_namespace)
        if default is not None:
            defaults[key_name] = deserialize[key_type](default.text)
        else:
            defaults[key_name] = None
        
        if key_type is not None and id is not None:
            key_types[id] = key_type
        else:
            pass
            #TODO: throw an error
            
        if key_name is not None and id is not None:
            key_names[id] = key_name
        else:
            pass
            #TODO: throw an error
            
    
    #need to do something much more sophisticated, but this will work for now
    for node in xml_root.findall('.//{%s}node' % graphml_namespace):
        v = g.add_vertex(convert_node_tag_to_node(node.attrib['id']))
        for key in vertex_keys:
            g.properties()[key][v] = defaults[key]
            
        for data in node.findall('.//{%s}data' % graphml_namespace):
            id = data.attrib['key']
            value = deserialize[key_types[id]](data.text)
            g.properties()[key_names[id]][v] = value
        
    for edge in xml_root.findall('.//{%s}edge' % graphml_namespace):
        e = g.add_edge(convert_node_tag_to_node(edge.attrib['source']),
                       convert_node_tag_to_node(edge.attrib['target'])
                       )  
        for key in edge_keys:
            g.properties()[key][e] = defaults[key]
        
        for data in edge.findall('.//{%s}data' % graphml_namespace):
            id = data.attrib['key']
            value = deserialize[key_types[id]](data.text)
            g.properties()[key_names[id]][e] = value
            
    return g



def write_graphml(g, 
                  f = sys.stdout,                   	
                  edge_default = 'undirected',
                  property_types = None,
                  property_fors = None
                  ):
    """
    property_types is a dict mapping graph properties to the type of
    their values. If not provided, the "attr.type" attribute of the
    "key" tag that defines properties in graphml isn't populated. yaupon
    allows for properties with arbitrary Python types as values, and
    properties can have non-uniform property value types, so "attr.type"
    isn't always relevant.

    property_fors is a dict similar to property_types: graphml requires
    that you have for="node" or for="edge" in the key definition. For
    a particular property p, if property_fors.get(p) is not None, we
    set for to property_fors[p]. Otherwise, if the property name begins
    with vertex/edge, we set the property that way. Otherwise, for defaults
    to "edge"
    """
    if property_types is None: property_types = {}
    if property_fors is None: property_fors = {}
    type_map = {'int':'int',
                'float':'double',
                'str':'string',
                'bool':'boolean'
                }
    
    xml_root = ET.Element('graphml')
    xml_root.attrib['xmlns'] = graphml_namespace
    xml_root.attrib['xmlns:xsi'] = graphml_namespace_xsi
    xml_root.attrib['xsi:schemaLocation'] = graphml_xsi_schema_location

    # Populate properties
    for i, (property_name, property) in enumerate(g.properties().items()):
        property_type = property_fors.get(property_name)
        if property_type is None:
            if property_name.startswith('vertex'):
                property_type = "node"
            else:
                property_type = "edge"
        xml_key = ET.Element('key')
        xml_key.attrib['id'] = '%s%s' % (property_type, i)
        xml_key.attrib['for'] = property_type
        xml_key.attrib['attr.name'] = property_name
        attr_type = property_types.get(property_name)
        if attr_type is not None:
            xml_key.attrib['attr.type'] = attr_type
        xml_root.append(xml_key)

    xml_graph = ET.Element('graph')
    xml_graph.attrib['id'] = 'G'
    xml_graph.attrib['edgedefault'] = edge_default

    for node in g.vertices():
        xml_node = ET.Element('node')
        xml_node.attrib['id'] = str(node)
        for i, (property_name, property) in enumerate(g.properties().items()):
            value = property.get(node)
            if value is None:
                continue
            xml_node_property = ET.Element('data')
            xml_node_property.attrib['key'] = 'node%s' % i
            xml_node_property.text = str(value)
            xml_node.append(xml_node_property)
        xml_graph.append(xml_node)

    for edge in g.edges():
        xml_edge = ET.Element('edge')
        xml_edge.attrib['source'] = str(edge[0])
        xml_edge.attrib['target'] = str(edge[1])
        for i, (property_name, property) in enumerate(g.properties().items()):
            value = property.get(edge)
            if value is None:
                continue
            xml_edge_property = ET.Element('data')
            xml_edge_property.attrib['key'] = 'edge%s' % i
            xml_edge_property.text = str(value)
            xml_edge.append(xml_edge_property)
        xml_graph.append(xml_edge)
    
    xml_root.append(xml_graph)
    f.write(ET.tostring(xml_root))
