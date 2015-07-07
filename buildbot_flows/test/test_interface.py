from buildbot_flows.interface_neo4j_json import (convert_node_container2json,
                                                 convert_json2node_container)

from buildbot_flows.data_nodes import flow

valid_flow = {
    "cost"    : 3.17,
    "version" : 0.2,
    "author"  : "unittest",
    "owner"   : "unittest",
    "description" : "unittest",
    "fulfillment" : "unittest",
}

expected_json_string = '''{
"author": "unittest", 
"cost": 3.17, 
"description": "unittest", 
"fulfillment": "unittest", 
"label": "flow", 
"owner": "unittest", 
"version": 0.2
}'''

def test_flow_to_json():
    node = flow(**valid_flow)
    js = convert_node_container2json(node,indent=0)
    assert(js == expected_json_string)

def test_json_to_flow():
    node1 = flow(**valid_flow)
    node2 = convert_json2node_container(expected_json_string)
    assert(node1 == node2)



