from buildbot_flows.neo_flows import enhanced_GraphDatabase

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}

gdb = enhanced_GraphDatabase(**neo4j_login)

def test_create_flow():
    gdb.new_flow(description = "TEST FLOW")

def test_flow_flow_relationship(): pass
def test_flow_validation_relationship(): pass
def test_create_validation(): pass

def test_flow_count_nodes(): pass
def test_flow_count_relationships(): pass

def test_flow_select(): pass
def test_flow_export_json(): pass

def test_flow_cost_propagation(): pass

