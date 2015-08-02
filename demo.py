'''
Neo4j flows workbench.
http://neo4j-rest-client.readthedocs.org/en/latest/info.html

Implementing flows as a graph database.
'''

from buildbot.graphDB import enhanced_GraphDatabase, hard_reset
from buildbot.utils import neo4j_credentials_from_env

if __name__ == "__main__":
    
    neo4j_login = neo4j_credentials_from_env()
    gdb = enhanced_GraphDatabase(**neo4j_login)
    
    flow = gdb.package.nodes["flow"]
    job  = gdb.package.nodes["job"]
    
    hard_reset(gdb)

    f1 = gdb.add_node(flow(description = u"Install neo4j-rest-client"))
    f2 = gdb.add_node(flow(description = u"pip install neo4jrestclient"))
    f3 = gdb.add_node(flow(description = u"Install pip"))
    f4 = gdb.add_node(flow(description = u"sudo apt-get install pip"))
    
    depends = gdb.package.relationships[("flow","depends","flow")]
    gdb.add_relationship(depends(f1,f2))
    gdb.add_relationship(depends(f2,f3))
    gdb.add_relationship(depends(f3,f4))

    job_required = gdb.package.relationships[("flow","requires","job")]
    developer = gdb.add_node(job(description = u"Developer"))
    system_admin = gdb.add_node(job(description = u"System Admin"))
    
    gdb.add_relationship(job_required(f3,developer,time=0.5))
    gdb.add_relationship(job_required(f2,developer,time=0.1))
    gdb.add_relationship(job_required(f4,system_admin,time=0.25))

    for node in gdb.iter_over("flow"):
        idx  = node["metadata"]["id"]
        desc = node["data"]["description"]
        cost = gdb.get_flow_total_time(idx)
        print "Cost {:0.3f} hrs, Action {}".format(cost, desc)

    msg = "{} known nodes, {} known relationships."
    print msg.format(gdb.count_nodes(), gdb.count_relationships())

    # Add some validation into the nodes
    f3["validation"] = u'''
    Run: `pip --version`
    Success: output should be > 7.0.3.
    Failure: command not found.
    '''

    f1["validation"] = u'''
    Run: `python -c "import neo4jrestclientx"`
    Success: Nothing
    Failure: ImportError: No module named neo4jrestclientx
    '''

    gdb.update_node(f1)
    gdb.update_node(f3)
    
