from buildbot_flows.interface_neo4j_json import (convert_node_container2json,
                                                 convert_json2node_container)

from buildbot_flows.data_nodes import flow

valid_flow = {
    "version" : 0.2,
    "description" : "unittest",
    "validation"  : "unittest",
}

expected_json_string = '''{
  "description": "unittest", 
  "label": "flow", 
  "validation": "unittest", 
  "version": 0.2
}'''.strip()

def test_flow_to_json():
    node = flow(**valid_flow)
    js = convert_node_container2json(node,indent=2)
    assert(js == expected_json_string)

def test_json_to_flow():
    node1 = flow(**valid_flow)
    node2 = convert_json2node_container(expected_json_string)
    assert(node1 == node2)



