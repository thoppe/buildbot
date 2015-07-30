import json

from data_schema import defined_nodes
from data_schema import defined_relationships

from generic_datatypes import node_container
from generic_datatypes import edge_container

_required_edge_members = ["start", "label", "end",
                          "start_id", "end_id", "id"]
_required_node_members = ["label", "id"]

def convert_neo4j2node(obj):
    '''
    Converts a neo4j result node into a buildbot node.
    Will validate:
    + That there is a exactly one label that overlaps with defined nodes.

    '''
    node_id = obj['metadata']['id']
    labelset = set(obj["metadata"]["labels"])

    if len(labelset.intersection(defined_nodes)) == 0:
        msg = "graphdb node {} requested is not a defined node"
        raise KeyError(msg.format(node_id))

    if len(labelset.intersection(defined_nodes)) > 1:
        msg = "graphdb node {} has ambiguous labeling"
        raise KeyError(msg.format(node_id))


    data = obj["data"]
    node = defined_nodes[labelset.pop()](**data)
    node.id = node_id
    return node

def convert_node_container2json(node, indent=2):
    '''
    Converts a generic node_container into a json object. Will validate:
    + It is a node_containter baseclass
    + The keys in .data and .obj_types are the same
    + Each type in .obj_types matches the that of .data

    If it passes, it turns the .data into a json object and adds the label
    as a new key.
    '''
    
    if node_container not in type(node).mro():
        msg = "convert_node_container2json expected a node_container"
        raise TypeError(msg)

    if not set(node.obj_types.keys()) == set(node.data.keys()):
        msg = ("convert_node_container2json received a malformed node. "
               ".data and .obj_keys did not match")
        raise TypeError(msg)

    for key in node:        
        if not node.validate_type(key, node[key]):
            msg = ("convert_node_container2json received a malformed node. "
                   "Key '{}' was not {}".format(key, node.obj_types[key]))
            raise TypeError(msg)

    # Create a copy of the data since we are going to add the label
    data = node.data.copy()

    for name in _required_node_members:
        data[name] = getattr(node, name)

    return json.dumps(data, indent=indent, sort_keys=True)


def convert_json2node_container(js, ignore_id_check=False):
    '''
    Converts a json string to a node_container json object. Will validate:
    + That js is a valid json string
    + That `label` exists as a key in js
    + That the label is a defined_node in generic_datatypes.py

    If it passes, it will return the proper subclassed node_container.
    '''
    try:
        data = json.loads(js)
    except ValueError as Ex:
        msg = "convert_json2node_container received malformed json {}"
        raise ValueError(msg.format(Ex))

    member_data = {}
    for name in _required_node_members:
        if ignore_id_check and name=="id":
            continue
        try:
            member_data[name] = data.pop(name)
        except KeyError:
            msg = "convert_json2node_container received json with no {}."
            raise KeyError(msg.format(name))

    label = member_data["label"]

    if label not in defined_nodes:
        msg = "{} is not a known node type."
        raise KeyError(msg.format(label))


    node = defined_nodes[label](**data)

    for name,value in member_data.items():
        setattr(node, name, value)

    return node


############################################################################

def convert_edge_container2json(edge, indent=2):
    '''
    Converts a generic node_container into a json object. Will validate:
    + It is a node_containter baseclass
    + The keys in .data and .obj_types are the same
    + Each type in .obj_types matches the that of .data

    If it passes, it turns the .data into a json object and adds the label
    as a new key.
    '''
    
    if edge_container not in type(edge).mro():
        msg = "convert_edge_container2json expected an edge_container"
        raise TypeError(msg)

    if not set(edge.obj_types.keys()) == set(edge.data.keys()):
        msg = ("convert_edge_container2json received a malformed edge. "
               ".data and .obj_keys did not match")
        raise TypeError(msg)

    for key in edge:        
        if not edge.validate_type(key, edge[key]):
            msg = ("convert_edge_container2json received a malformed edge. "
                   "Key '{}' was not {}".format(key, edge.obj_types[key]))
            raise TypeError(msg)

    # Create a copy of the data since we are going to add start,label,end
    data = edge.data.copy()

    for key in _required_edge_members:
        data[key] = getattr(edge,key)

    return json.dumps(data, indent=indent, sort_keys=True)

def convert_json2edge_container(js):
    '''
    Converts a json string to a edge_container json object. Will validate:
    + That js is a valid json string
    + That start_id,rel,end_id exists as a key in js
    + That the start_id,rel,end_id is a defined_edge in generic_datatypes.py

    If it passes, it will return the proper subclassed edge_container.
    '''
    try:
        data = json.loads(js)
    except ValueError as Ex:
        msg = "convert_edge_container2json received malformed json {}"
        raise ValueError(msg.format(Ex))

    member_data = {}

    for name in _required_edge_members:
        try:
            member_data[name] = data.pop(name)
        except KeyError:
            msg = "convert_edge_container2json received json with no {}."
            raise KeyError(msg.format(name))

    key = (member_data["start"],
           member_data["label"],
           member_data["end"])    

    if key not in defined_relationships:
        msg = "{} is not a known relationship type."
        raise KeyError(msg.format(key))


    edge = defined_relationships[key](member_data["start_id"],
                                      member_data["end_id"],**data)

    for name,value in member_data.items():
        setattr(edge, name, value)

    return edge
                                      

