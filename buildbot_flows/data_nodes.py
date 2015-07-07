'''
Each node in the graphdb is a contract that the following fields will
exist, be of the type listed, and will be populated with the default
value if none is given.
'''

from generic_datatypes import node_container

class flow(node_container):
    label = "flow"
    _object_defaults = {
        "cost"    : 0.00,
        "version" : 1.0,
        "author"  : "",
        "owner"   : "",
        "description" : "",
        "fulfillment" : "",
    }


class validation(node_container):
    label = "validation"
    _object_defaults = {
        "command"  : "",
        "success"  : "",
        "failure"  : "",
    }


defined_nodes = {
    "flow" : flow,
    "validation" : validation,
}

