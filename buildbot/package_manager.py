'''
Nodes are dynamicaly loaded into the namespace with this module.
'''

import json

from generic_datatypes import node_container
from generic_datatypes import edge_container

class buildbot_package(object):

    def __init__(self, string_input):
        self.load_package(string_input)

    def update(self, other_package):
        self.nodes.update(other_package.nodes)
        self.relationships.update(other_package.relationships)

    def load_package(self, string_input):
        js = json.loads(string_input)
        
        self.nodes = {}
        self.relationships = {}

        if "requires" in js:
            for filename in js["requires"]:
                with open(filename,'r') as FIN:
                    raw = FIN.read()
                    px = buildbot_package(raw)
                    self.update(px)

        for key,val in js["nodes"].items():
            self.add_node(key, val)

        for item in js["relationships"]:
            self.add_relationship(item)
    
    def add_node(self, key, data):        
        class _node_factory(node_container):
            label = key
            _object_defaults = data

        self.nodes[key] = _node_factory

    def add_relationship(self, item):
        data = {}
        if len(item)<3:
            msg = ("Relationships need at least three items\n"
                   "source label target {attributes}")
            raise ValueError(msg)
        source   = item.pop(0)
        rel_name = item.pop(0)
        target   = item.pop(0)
        try   : data = item.pop(0)
        except: data = {}

        # Check that relationship nodes are defined
        msg = "'{}' node has not been defined in the package."
        if source not in self.nodes:
            raise ValueError(msg.format(source))
        if target not in self.nodes:
            raise ValueError(msg.format(source))
                    
        class _rel_factory(edge_container):
            start = source
            end   = target
            label = rel_name
            _object_defaults = data

        key = (_rel_factory.start,
               _rel_factory.label,
               _rel_factory.end)

        self.relationships[key] = _rel_factory



#f_flows = "packages/flows.json"
f_flows = "packages/project_management.json"

with open(f_flows) as FIN:
    raw = FIN.read()

P = buildbot_package(raw)

print P

#############################################################
# Flow nodes
#############################################################

#############################################################
# Organizational nodes
#############################################################

#############################################################
# SCRUM nodes
#############################################################

'''
#############################################################
Allowed relationships, read as (A)->[is]->(B). Defined in this way 
so everything is explict and properities can be added later.
#############################################################
'''

#############################################################
# Node label mappings for imports
#############################################################

'''

import sys
import inspect
import collections

class_introspection = inspect.getmembers(sys.modules[__name__],
                                         inspect.isclass)

# Programmatically construct the defined nodes from above
defined_nodes = {}
for name,cls in class_introspection:
    if node_container in cls.mro() and cls is not node_container:
        defined_nodes[name] = cls

# Programmatically construct the relationships
defined_relationships = collections.defaultdict(dict)
for name,cls in class_introspection:
    if edge_container in cls.mro() and cls is not edge_container:
        key = (cls.start, cls.label, cls.end)
        defined_relationships[key] = cls
defined_relationships = dict(defined_relationships)
'''
