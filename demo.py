'''
Neo4j flows workbench.
http://neo4j-rest-client.readthedocs.org/en/latest/info.html

In-progress experiment implementing flows as a graph database.
'''

from buildbot_flows.neo_flows import enhanced_GraphDatabase
from buildbot_flows.data_nodes import flow, validation

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}


if __name__ == "__main__":

    gdb = enhanced_GraphDatabase(**neo4j_login)
    #gdb.hard_reset()

    x = flow()
    print x.data
    


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

    

