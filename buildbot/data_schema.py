'''
Each node in the graphdb is a contract that the following fields will
exist, be of the type listed, and will be populated with the default
value if none is given.
'''

from generic_datatypes import node_container
from generic_datatypes import edge_container
import time


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


# Helper function to create an edge from defined nodes
def create_relationship_object(node1, relationship, node2,
                               *args, **kwargs):
    key = (node1.label, relationship, node2.label)
    if key not in defined_relationships:
        msg = "{} -[{}]> {} is an invalid relationship"
        raise KeyError(msg.format(*key))
    return defined_relationships[key](*args, **kwargs)
