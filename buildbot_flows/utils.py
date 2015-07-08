from neo4jrestclient.client import GraphDatabase

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}

gdb = GraphDatabase(**neo4j_login)

def build_meta_graph():
    '''
    Exports a JSON graph that explains all known relationship types and nodes.
    '''

    from data_schema import defined_nodes
    from data_schema import defined_relationships

    meta = gdb.labels.create("meta_description")
    
    NODES = {}
    for name in defined_nodes:
        node = gdb.node(name=name)
        NODES[name] = node
        meta.add(node)
     
    for start_key in defined_relationships:
        for rel, end_key in defined_relationships[start_key]:
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
    raw_input()
    clean_meta_graph()
    
    
