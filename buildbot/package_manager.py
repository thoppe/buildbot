'''
Nodes are dynamicaly loaded into the namespace with this module.
'''

import json

from generic_datatypes import node_container
from generic_datatypes import edge_container
from contract_manager  import buildbot_contract, buildbot_action
import peacock


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

    def add_node(self, key, data):

        # Extract any json-LD context information (marked by @ keys)        
        context = {}
        for data_key in data.keys():
            if data_key and data_key[0]=="@":
                context[data_key] = data.pop(data_key)
        
        class _node_factory(node_container):
            label = key
            _object_defaults = data
            _context = context

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

###################################################################
def minimal_peacock():
    ''' Return a minimal working swagger file object (peacock) '''
    info = peacock.Info(title="",version="")
    return peacock.Swagger(info=info,
                           paths=peacock.Paths())

def export_package_to_swagger(p):
    type_lookup = {
        int:"integer",
        float:"number",
        bool:"boolean",
        str:"string",
        unicode:"string",
    }
    
    S = minimal_peacock()
    S.info.title   = p.meta["title"]
    S.info.version = p.meta["version"]
    S.info.description = p.meta["description"]
    S.info.contact = peacock.Contact(name=p.meta["author"])

    defs = []
    for key,node in p.nodes.items():
        
        props = {}
        for name,val in node._object_defaults.items():
            obj_type = type_lookup[type(val)]
            props[name] = peacock.Property(type_=obj_type)
            
        props  = peacock.Properties(props)
        
        schema = peacock.Schema(type_="object",
                                properties=props)
        defs.append(schema)
    
    defs = zip(p.nodes, defs)
    S.definitions = peacock.Definitions(defs)
    
    print S
    exit()

###################################################################



if __name__ == "__main__":
    f_package = "packages/checkin/checkin.json"

    with open(f_package) as FIN:
        raw = FIN.read()

    P = buildbot_package(raw)
    export_package_to_swagger(P)
