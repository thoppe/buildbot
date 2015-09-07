import json

from generic_datatypes import node_container
from generic_datatypes import edge_container

_required_edge_members = ["start", "label", "end",
                          "start_id", "end_id", "id"]
_required_node_members = ["label", "id"]

def convert_neo4j2node_container(obj,package):
    '''
    Converts a neo4j result node into a buildbot node.
    Will validate:
    + That there is a exactly one label that overlaps with packages nodes.

    '''
    node_id = obj['metadata']['id']
    labelset = set(obj["metadata"]["labels"])

    if len(labelset.intersection(package.nodes)) == 0:
        msg = "graphdb node {} requested is not defined in the package"
        raise KeyError(msg.format(node_id))

    if len(labelset.intersection(package.nodes)) > 1:
        msg = "graphdb node {} has ambiguous labeling"
        raise KeyError(msg.format(node_id))


    data = obj["data"]
    node = package.nodes[labelset.pop()](**data)
    node.id = node_id
    return node


def convert_json2node_container(js, package, ignore_id_check=False):
    '''
    Converts a json string to a node_container json object. Will validate:
    + That js is a valid json string
    + That `label` exists as a key in js
    + That the label is a defined in the package.

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

    if label not in package.nodes:
        msg = "{} is not a known node type."
        raise KeyError(msg.format(label))

    node = package.nodes[label](**data)

    for name,value in member_data.items():
        node[name] = value

    return node


############################################################################

def convert_json2edge_container(js, package, ignore_id_check=False):
    '''
    Converts a json string to a edge_container json object. Will validate:
    + That js is a valid json string
    + That start_id,rel,end_id exists as a key in js
    + That the start_id,rel,end_id is in the package.

    If it passes, it will return the proper subclassed edge_container.
    '''
    try:
        data = json.loads(js)
    except ValueError as Ex:
        msg = "convert_json2edge_container received malformed json {}"
        raise ValueError(msg.format(Ex))

    member_data = {}

    for name in _required_edge_members:
        if ignore_id_check and name=="id":
            continue
        try:
            member_data[name] = data.pop(name)
        except KeyError:
            msg = "convert_json2edge_container received json with no {}."
            raise KeyError(msg.format(name))

    key = (member_data["start"],
           member_data["label"],
           member_data["end"])    

    if key not in package.relationships:
        msg = "{} is not a known relationship type."
        raise KeyError(msg.format(key))


    edge = package.relationships[key](member_data["start_id"],
                                      member_data["end_id"],**data)

    for name,value in member_data.items():
        setattr(edge, name, value)

    return edge
                                      

############################################################################
# To do at some point (class-ify this whole package manager mess)
# class neo4j2containers(object):
    
