'''
Neo4j flows workbench.
http://neo4j-rest-client.readthedocs.org/en/latest/info.html

In-progress experiment implementing flows as a graph database.
'''

from buildbot.neo_flows import enhanced_GraphDatabase
from buildbot.data_schema import flow

from buildbot.data_schema import defined_relationships
from buildbot.data_schema import defined_nodes
from buildbot.data_schema import create_relationship_object

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}


if __name__ == "__main__":

    gdb = enhanced_GraphDatabase(**neo4j_login)
    
    description = "UNITTEST -- delete when complete."

    a = defined_nodes["flow"](description=description)
    b = defined_nodes["flow"](description=description)
    gdb.add_node(a)
    gdb.add_node(b)

    x = defined_relationships[("flow","depends","flow")](a,b)
    gdb.add_relationship(x)
    print x
    print a
    exit()
    #x = create_relationship_object(a,"depends",b)
    print vars(a)
    exit()
    gdb.add_relationship(x)
    print x
    #ab = defined_
    #print a
    #gdb.connect(a,b)
    #print a,b
    exit()

    f1 = gdb.new_flow(description = "Install neo4j-rest-client")
    f2 = gdb.new_flow(description = "Install pip")
    f3 = gdb.new_flow(description = "sudo apt-get install pip", cost=0.25)
    f4 = gdb.new_flow(description = "pip install neo4jrestclient", cost=0.10)

    f1.relationships.create("depends", f2)
    f2.relationships.create("depends", f3)
    f1.relationships.create("depends", f4)

    v = gdb.new_validation(
        command="pip --version",
        success="pip 7.0.3 ...",
        failure="command not found",
        )

    f2.relationships.create("validator", v)

    v = gdb.new_validation(
        command='python -c "import neo4jrestclientx"',
        success="",
        failure="ImportError: No module named neo4jrestclientx",
        )

    v.relationships.create("validator", f1)

    for node in gdb.iter_over("flow"):
        idx  = node["metadata"]["id"]
        desc = node["data"]["description"]
        cost = gdb.get_total_cost(idx)
        print "Cost {:0.3f} hrs, Action {}".format(cost, desc)

    msg = "{} known nodes, {} known relationships."
    print msg.format(gdb.count_nodes(), gdb.count_relationships())

    key = "Install neo4j-rest-client"
    idx = gdb.select('flow', description=key, author="")

    #print gdb.export_json(idx)

    

