'''
Each node in the graphdb is a contract that the following fields will
exist, be of the type listed, and will be populated with the default
value if none is given.
'''

from generic_datatypes import node_container
import time


#############################################################
# Flow nodes
#############################################################

class flow(node_container):
    label = "flow"
    _object_defaults = {
        "version" : 1.0,
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


#############################################################
# Allowed relationships, read as (A)->[is]->(B)
#############################################################

defined_relationships = {
    "flow" : [
        ("depends" , "flow"),
        ("fork"    , "flow"),
        ("satisfy" , "objective"),
        ("requires", "job"),
        ("requires", "asset"),
    ],
    
    "person" : [
        ("assigned", "task"),
        ("owns"    , "flow"),
        ("skilled" , "job"),
    ],
    
    "task" : [
        ("satisfy" , "flow"),
        ("assigned", "sprint"),
    ],
    
    "organization": [
        ("has" , "objective"),
        ("has" , "person"),
        ("has" , "project"),
    ],

    "project" : [
        ("has" , "flow"),
        ("has" , "project"),
    ],

}


#############################################################
# Node label mappings for imports
#############################################################

defined_nodes = {
    "flow"  : flow,
    "job"   : job,
    "asset" : asset,

    "organization" : organization,
    "objective" : objective,
    "person" : person,
    "project"      : project,
    
    "task" : task,
    "sprint" : sprint,
}



