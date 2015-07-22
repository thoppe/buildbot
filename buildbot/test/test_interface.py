import buildbot.interface_neo4j_json as interface
from buildbot.data_schema import defined_relationships
from buildbot.data_schema import defined_nodes

test_flow_data = {
    "version"     : 0.2,
    "description" : "unittest",
    "validation"  : "unittest",
    "status"      : 0.75,
    "id" : 7,
}

test_job_data = {
    "title" : "Slacker",
    "description" : "Do nothing all day",
    "id" : 8,
}

test_requires_data = {
    "time" : 3.7,
    "id": 22,
}
    
flow = defined_nodes["flow"]
job  = defined_nodes["job"]
requires = defined_relationships[("flow","requires","job")]

def test_flow_to_json_to_flow():
    node1     = flow(**test_flow_data)
    json_text = interface.convert_node_container2json(node1,indent=2)
    node2     = interface.convert_json2node_container(json_text)

    assert( node1 == node2 )
    assert( node1.id == node2.id )


def test_relationship_to_json():
    node1     = flow(**test_flow_data)
    node2     = job (**test_job_data)
    edge1 = requires(node1,node2, **test_requires_data)
    
    json_text = interface.convert_edge_container2json(edge1,indent=2)
    edge2     = interface.convert_json2edge_container(json_text)
    
    assert( edge1 == edge2 )
    assert( edge1.id == edge2.id )


