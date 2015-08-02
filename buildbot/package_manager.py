'''
Nodes are dynamicaly loaded into the namespace with this module.
'''

import time
import collections
import json
import ast
import sys

from generic_datatypes import node_container
from generic_datatypes import edge_container

    #code = ''class {function_name}(_is_subgraph_free):\n\tsubg = {subgraph}
    #''.format(function_name=full_name, subgraph=input_subg).strip()
    #return code
        
    #class x(_is_subgraph_free):
    #    subg = input_subg
    # setattr(thismodule, full_name, x)


class buildbot_package(object):

    def __init__(self, string_input):
        self.load_package(string_input)

    def load_package(self, string_input):
        js = json.loads(string_input)
        
        self.nodes = {}
        self.relationships = {}

        for key,val in js["nodes"].items():
            self.add_node(key, val)

        for item in js["relationships"]:
            self.add_relationship(item)                
            
        print self.nodes
        print self.relationships
        exit()

    def process_type(self, obj):
        try:
            val = ast.literal_eval(obj)
        except:
            msg = "Object {} can't be literally interperted as a python object"
            raise ValueError(msg.format(obj))
        return val
    
    def add_node(self, key, val):
        data = {}
        for name, obj in val.items():
            data[name] = self.process_type(obj)
        
        class _node_factory(node_container):
            label = key
            _object_defaults = data

        self.nodes[key] = _node_factory

    def add_relationship(self, item):
        data = {}
        if len(item)<3:
            msg = ("Relationships need at least three items\n"
                   "source label target (attributes)")
            raise ValueError(msg)
        source   = item.pop(0)
        rel_name = item.pop(0)
        target   = item.pop(0)
        try   : attrs = item.pop(0)
        except: attrs = {}

        data = {}
        for name, obj in attrs.items():
            data[name] = self.process_type(obj)
        
            
        class _rel_factory(edge_container):
            start = source
            end   = target
            label = rel_name
            _object_defaults = data

        key = (_rel_factory.start,
               _rel_factory.label,
               _rel_factory.end)

        self.relationships[key] = _rel_factory



f_flows = "packages/flows.json"
with open(f_flows) as FIN:
    raw = FIN.read()

P = buildbot_package(raw)

#for key in js["nodes"]:
#    P.load_node(key, js)
#    print key


exit()
#############################################################
# Flow nodes
#############################################################

class flow(node_container):
    label = "flow"
    _object_defaults = {
        "version" : 1.0,
        "status"  : 0.0,
        "description" : "",
        "validation" : "",
    }

class job(node_container):
    label = "job"
    _object_defaults = {
        "description" : "",
        "title" : "",
    }

class asset(node_container):
    label = "asset"
    _object_defaults = {
        "description" : "",
        "title" : "",
    }

#############################################################
# Organizational nodes
#############################################################

class organization(node_container):
    label = "organization"
    _object_defaults = {
        "name" : "",
        "description" : "",
    }
        
class objective(node_container):
    label = "objective"
    _object_defaults = {
        "description" : "",
    }

class person(node_container):
    label = "person"
    _object_defaults = {
        "name" : "",
        "username" : "",
        "userid" : 0,
    }

# Projects have a start and end time which defaults to now and approximately one day from now
class project(node_container):
    label = "project"
    _object_defaults = {
        "name" : "",
        "description" : "",
        "starttime" : time.time(),
        "endtime"   : time.time()*10**7,
   }
        

#############################################################
# SCRUM nodes
#############################################################

class task(node_container):
    label = "task"
    _object_defaults = {
        "name" : "",
        "description" : "",
    }

class sprint(node_container):
    label = "sprint"
    _object_defaults = {
        "name" : "",
        "description" : "",
    }


'''
#############################################################
Allowed relationships, read as (A)->[is]->(B). Defined in this way 
so everything is explict and properities can be added later.
#############################################################
'''

class flow_depends_flow(edge_container):
    start = "flow"
    label = "depends"
    end   = "flow"

class flow_fork_flow(edge_container):
    start = "flow"
    label = "fork"
    end   = "flow"
    
class flow_satisfy_objective(edge_container):
    start = "flow"
    label = "satisfy"
    end   = "objective"

class flow_requires_job(edge_container):
    start = "flow"
    label = "requires"
    end   = "job"

    _object_defaults = {
        "time" : 0.0
    }

class flow_requires_asset(edge_container):
    start = "flow"
    label = "requires"
    end   = "asset"

    _object_defaults = {
        "cost" : 0.0
    }

class person_assigned_task(edge_container):
    start = "person"
    label = "assigned"
    end   = "task"

class person_owns_flow(edge_container):
    start = "person"
    label = "owns"
    end   = "flow"

class person_skilled_job(edge_container):
    start = "person"
    label = "skilled"
    end   = "job"

class task_satisfy_flow(edge_container):
    start = "task"
    label = "satisfy"
    end   = "flow"

class task_assigned_sprint(edge_container):
    start = "task"
    label = "assigned"
    end   = "sprint"

class organization_has_objective(edge_container):
    start = "organization"
    label = "has"
    end   = "objective"

class organization_has_person(edge_container):
    start = "organization"
    label = "has"
    end   = "person"

class organization_has_asset(edge_container):
    start = "organization"
    label = "has"
    end   = "asset"
    
class organization_has_project(edge_container):
    start = "organization"
    label = "has"
    end   = "project"

class project_has_flow(edge_container):
    start = "project"
    label = "has"
    end   = "flow"
    
class project_has_project(edge_container):
    start = "project"
    label = "has"
    end   = "project"

#############################################################
# Node label mappings for imports
#############################################################

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
