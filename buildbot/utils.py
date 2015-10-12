import os
from neo4jrestclient.client import GraphDatabase

def get_env_variable(key):
    val = os.environ.get(key,None)
    if val is None:
        msg = "Environment variable {} not set!".format(key)
        raise KeyError(msg)
    return val

def neo4j_credentials_from_env(**kwargs):
    cred = {}

    env_keys = {
        "auth"    : "NEO4J_AUTH",
        "port": "NEO4J_TCP_PORT",
        "addr": "NEO4J_TCP_ADDR",
        "f_package" : "buildbot_package",
    }

    for key,name in env_keys.items():
        if name in kwargs:
            cred[key] = kwargs[name]
        else:
            cred[key] = get_env_variable(name)
        
    username, password = cred["auth"].split(':')

    return {
        "username" : username,
        "password" : password,
        "url" : "http://{}:{}".format(cred["addr"], cred["port"]),
        "buildbot_package" : cred["f_package"],
    }

grassfile = '''
node {
  diameter: 75px;
  border-color: #9AA1AC;
  border-width: 2px;
  text-color-internal: #222222;
  font-size: 12px;
}

relationship {
  font-size: 12px;
  padding: 4px;
  caption: '<type>';

  color: #333333;
  border-color: #BF85D6;
  text-color-internal: #FFFFFF;

  shaft-width: 3px;
}

meta_description {
  color: #A5ABB6;
  shaft-width: 10px;
  font-size: 8px;
  padding: 3px;
  text-color-external: #000000;
  text-color-internal: #FFFFFF;
  caption: '<type>';
}
'''


def build_meta_graph(gdb):
    '''
    Exports a JSON graph that explains all known relationship types and nodes.
    '''
    meta = gdb.labels.create("meta_description")

    defined_nodes = gdb.package.nodes
    defined_relationships = gdb.package.relationships
    
    NODES = {}
    for name in defined_nodes:
        print "Adding node", name
        node = gdb.node(name=name)
        NODES[name] = node
        meta.add(node)
     
    for start_key, rel, end_key in defined_relationships:
        print "Adding relationship", start_key,rel,end_key
        v0 = NODES[start_key]
        v1 = NODES[end_key]
        gdb.relationships.create(v0,rel,v1)

def clean_meta_graph(gdb):

    # Remove all the meta_descriptions
    q = '''
    MATCH (n:meta_description)
    OPTIONAL MATCH (n)-[r]-()
    DELETE n,r
    '''

    result = gdb.query(q,data_contents=True).stats
    print "Meta clean: "
    print "{relationship_deleted} relationships".format(**result)
    print "{nodes_deleted} nodes".format(**result)


if __name__ == "__main__":
    from graphDB import enhanced_GraphDatabase
    
    neo4j_login = neo4j_credentials_from_env()
    gdb = enhanced_GraphDatabase(**neo4j_login)
    
    clean_meta_graph(gdb)
    build_meta_graph(gdb)
    msg = ("Visit http://localhost:7474/browser/ to see the schema;"
           "\n Enter to Exit")
    raw_input(msg)
    clean_meta_graph(gdb)
    
