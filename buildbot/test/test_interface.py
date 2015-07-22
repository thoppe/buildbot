from buildbot.interface_neo4j_json import (convert_node_container2json,
                                           convert_json2node_container)
from buildbot.data_schema import defined_relationships
from buildbot.data_schema import defined_nodes

test_flow_data = {
    "version"     : 0.2,
    "description" : "unittest",
    "validation"  : "unittest",
    "status"      : 0.75,
}

flow = defined_nodes["flow"]

def test_flow_to_json_to_flow():
    node1     = flow(**test_flow_data)
    json_text = convert_node_container2json(node1,indent=2)
    node2     = convert_json2node_container(json_text)
    assert( node1 == node2 )


