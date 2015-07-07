import json
from generic_datatypes import node_container
from data_nodes import defined_nodes

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
    data["label"] = node.label

    return json.dumps(data, indent=indent, sort_keys=True)


def convert_json2node_container(js):
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
        msg = "convert_node_container2json received malformed json {}"
        raise ValueError(msg.format(Ex))

    try:
        label = data.pop("label")
    except KeyError:
        msg = "convert_node_container2json received json with no label."
        raise KeyError(msg)

    if label not in defined_nodes:
        msg = "{} is not a known node type."
        raise KeyError(msg.format(label))

    return defined_nodes[label](**data)
