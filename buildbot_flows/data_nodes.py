'''
Each node in the graphdb is a contract that the following fields will
exist, be of the type listed, and will be populated with the default
value if none is given.
'''

from generic_datatypes import node_container

class flow(node_container):
    label = "flow"
    _object_defaults = {
        "version" : 1.0,
        "description" : "",
        "validation" : "",
    }

#############################################################

defined_nodes = {
    "flow" : flow,
}

defined_relationships = {
    "flow" : {
        "depends" : "flow",
        "fork"    : "flow",
    },

}

