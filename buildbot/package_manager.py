'''
Nodes are dynamicaly loaded into the namespace with this module.
'''

import json
import peacock

from generic_datatypes import node_container
from generic_datatypes import edge_container
from contract_manager  import buildbot_contract, buildbot_action

# TO DO: let a buildbot_package be constrained by traits
from traits.api import Int, Str, Float, List, Enum
from traits.api import Bool, Any, Dict, Either, This
from traits.api import Instance, HasTraits

class buildbot_package(object):

    def __init__(self, string_input):
        self.load_package(string_input)        

    def __repr__(self):
        data = {
            "nodes":self.nodes.keys(),
            "relationships":self.relationships.keys(),
            "contracts":self.contracts.keys(),
            "actions":self.actions.keys(),
        }
        return json.dumps(data,indent=1)

    def update(self, other_package):
        self.nodes.update(other_package.nodes)
        self.relationships.update(other_package.relationships)

    def load_package(self, string_input):
        js = json.loads(string_input)
        
        self.nodes = {}
        self.relationships = {}
        self.contracts = {}
        self.actions = {}

        if "code_entry" in js:
            self.code_entry = js["code_entry"]
        else:
            self.code_entry = ""

        if "requires" in js:
            for filename in js["requires"]:
                with open(filename,'r') as FIN:
                    raw = FIN.read()
                    px = buildbot_package(raw)
                    self.update(px)
                    
        if "meta" in js:
            self.meta = js["meta"]

        for key,val in js["nodes"].items():
            self.add_node(key, val)

        for item in js["relationships"]:
            self.add_relationship(item)

        # Load the contracts if they exist
        if "contracts" in js:
            for name in js["contracts"]:
                self.contracts[name] = buildbot_contract(name)

        # Load the actions if they exist
        if "actions" in js:
            for name,data in js["actions"].items():
                self.actions[name] = buildbot_action(name,data,self)

    def add_node(self, key, schema_data):

        # Extract any json-LD context information (marked by @ keys)        
        context = {}
        for data_key in schema_data.keys():
            if data_key and data_key[0]=="@":
                context[data_key] = schema_data.pop(data_key)

        # Create a class instance for the node
        node = node_container(label=key, **schema_data)

        self.nodes[key] = node

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

        data["label"] = rel_name
        data["start"] = source
        data["end"]   = target

        edge = edge_container(**data)

        key = (data["start"],
               data["label"],
               data["end"])

        self.relationships[key] = edge

###################################################################

type_lookup = {
    int:"integer",
    float:"number",
    bool:"boolean",
    str:"string",
    unicode:"string",
}

def build_operation(node,**kwargs):

    desc = "A {name} node.".format(**kwargs)
    pass_response = peacock.Response(description=desc)
    all_responses = peacock.Responses({"200":pass_response})

    desc = "{verb} a {name} node.".format(**kwargs)
    op = peacock.Operation(description=desc,
                           responses=all_responses)
    
    return op

def export_package_to_swagger(p):

    S = peacock.Swagger()
    S.info.title   = p.meta["title"]
    S.info.version = p.meta["version"]
    S.info.description = p.meta["description"]
    S.info.contact = peacock.Contact(name=p.meta["author"])

    # Definitions taken from package nodes
    S.definitions = defs = peacock.Definitions()

    for key,node in p.nodes.items():
        defs[key] = peacock.Schema(type000="object")

        for name,obj_type in node._object_types.items():
            swagger_type = type_lookup[obj_type]
            prop = peacock.Property(type000=swagger_type) 
            defs[key].properties[name] = prop

    # Assign the operations

    for key,node in p.nodes.items():
        
        get_id,create,delete = [peacock.Operation() for x in range(3)]
        
        #get.description = "Retrieves a node by index."
        #get.responses["200"] = peacock.Response()
        #get.responses["200"].description = "Returns a {} node.".format(key)
        #get.produces = ["application/json"]

        ref = "#/definitions/{}".format(key)        

        # Create NODE
        url = "/node/{}/create".format(key)
        path = peacock.Path()
        path.post = peacock.Operation()
        path.post.description = "Creates a {} node.".format(key)
        para = peacock.Parameter(name=key, in000="body")
        para.description = "{} node to add.".format(key)
        para.required = True
        para.schema = peacock.Schema(ref000=ref)       
        path.post.parameters.append(para)
        S.paths[url] = path

        # Update NODE
        url = "/node/{}/update".format(key)
        path = peacock.Path()
        path.post = peacock.Operation()
        path.post.description = "Updates a {} node.".format(key)
        para = peacock.Parameter(name=key, in000="body")
        para.description = "{} node to update.".format(key)
        para.required = True
        para.schema = peacock.Schema(ref000=ref)       
        path.post.parameters.append(para)
        S.paths[url] = path

        # Remove NODE
        url = "/node/{}/remove".format(key)
        path = peacock.Path()
        path.post = peacock.Operation()
        path.post.description = "Deletes a {} node.".format(key)
        para = peacock.Parameter(name=key, in000="body")
        para.description = "{} node to delete.".format(key)
        para.required = True
        para.schema = peacock.Schema(ref000=ref)       
        path.delete.parameters.append(para)
        S.paths[url] = path

        # Get single NODE
        url = "/node/{}".format(key)
        path = peacock.Path()
        path.post = peacock.Operation()
        path.post.description = "Gets a single {} node.".format(key)
        para = peacock.Parameter(name="id", in000="body")
        para.description = "{} node to get.".format(key)
        para.required = True
        path.get.parameters.append(para)
        S.paths[url] = path

        # Search for a NODE
        url = "/node/{}/search".format(key)
        path = peacock.Path()
        path.post = peacock.Operation()
        path.post.description = "Searchs for a node.".format(key)
        para = peacock.Parameter(name="id", in000="body")
        para.description = "{} node to get.".format(key)
        para.required = True
        path.get.parameters.append(para)
        S.paths[url] = path

        # Create RELATIONSHIP [TODO]
        # Delete RELATIONSHIP [TODO]                
        # Add in tasks [TODO]
        
    return S

###################################################################



if __name__ == "__main__":
    f_package = "packages/checkin/checkin.json"

    with open(f_package) as FIN:
        raw = FIN.read()

    P = buildbot_package(raw)
    S = export_package_to_swagger(P)
    print S
