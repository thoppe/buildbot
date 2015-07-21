'''
Neo4j flows workbench.
http://neo4j-rest-client.readthedocs.org/en/latest/info.html

In-progress experiment implementing flows as a graph database.
'''

from buildbot.neo_flows import enhanced_GraphDatabase, hard_reset
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

    flow = defined_nodes["flow"]
    job  = defined_nodes["job"]

    hard_reset(gdb)

    developer = gdb.add_node(job(description = "Developer"))

    #f1 = gdb.add_node(flow(description = "Install neo4j-rest-client"))
    #f2 = gdb.add_node(flow(description = "pip install neo4jrestclient"))
    #f3 = gdb.add_node(flow(description = "Install pip"))
    f4 = gdb.add_node(flow(description = "sudo apt-get install pip"))

    #depends = defined_relationships[("flow","depends","flow")]
    #gdb.add_relationship(depends(f1,f2))
    #gdb.add_relationship(depends(f2,f3))
    #gdb.add_relationship(depends(f3,f4))

    job_required = defined_relationships[("flow","requires","job")]
    #gdb.add_relationship(job_required(f2,developer,time=0.5))
    gdb.add_relationship(job_required(f4,developer,time=0.1))

    '''
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
    '''

    gdb.get_total_cost(f4.id)
    exit()

    for node in gdb.iter_over("flow"):
        idx  = node["metadata"]["id"]
        desc = node["data"]["description"]
        cost = gdb.get_total_cost(idx)
        print "Cost {:0.3f} hrs, Action {}".format(cost, desc)
    exit()

    msg = "{} known nodes, {} known relationships."
    print msg.format(gdb.count_nodes(), gdb.count_relationships())

    key = "Install neo4j-rest-client"
    idx = gdb.select('flow', description=key, author="")

    #print gdb.export_json(idx)

    

