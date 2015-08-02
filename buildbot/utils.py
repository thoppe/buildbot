import os
from neo4jrestclient.client import GraphDatabase

def get_env_variable(key):
    val = os.environ.get(key,None)
    if val is None:
        msg = "Environment variable {} not set!".format(key)
        raise KeyError(msg)
    return val

def neo4j_credentials_from_env():
    user_pass = get_env_variable("NEO4J_ENV_NEO4J_AUTH")
    username, password = user_pass.split(':')
    tcp_addr = get_env_variable("NEO4J_PORT_7474_TCP_ADDR")
    tcp_port = get_env_variable("NEO4J_PORT_7474_TCP_PORT")
    
    return {
        "username" : username,
        "password" : password,
        "url" : "http://{}:{}".format(tcp_addr, tcp_port)
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


def build_meta_graph():
    '''
    Exports a JSON graph that explains all known relationship types and nodes.
    '''

    from data_schema import defined_nodes
    from data_schema import defined_relationships

    gdb = GraphDatabase(**neo4j_login)
    meta = gdb.labels.create("meta_description")
    
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

def clean_meta_graph():

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
    clean_meta_graph()
    build_meta_graph()
    raw_input("Visit http://localhost:7474/browser/ to see the schema; Enter to Exit")
    clean_meta_graph()
    
    
