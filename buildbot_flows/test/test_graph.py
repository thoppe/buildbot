from nose.tools import *
from unittest import TestCase

from buildbot_flows.neo_flows import enhanced_GraphDatabase
from buildbot_flows.data_nodes import flow

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}

class test_neo4j_graph(TestCase):
    test_owner = "UNITTEST"
    
    def setUp(self):
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
    
    def tearDown(self):
        q = '''
        MATCH n
        WHERE n.owner="{}"
        DELETE n;
        '''.format(self.test_owner)
        result = self.gdb.query(q, data_contents=True)
        print result.stats["nodes_deleted"],

    def test_add_flow(self):
        # Create a flow node, return the idx created.
        node = flow(owner=self.test_owner)
        return self.gdb.add(node)

    def test_remove_node_by_index(self):
        idx = self.test_add_flow()
        result = self.gdb.remove(idx)
        assert(result["nodes_deleted"] == 1)

    @raises(Exception)
    def test_remove_missing_node(self):
        idx = self.test_add_flow()
        result = self.gdb.remove(idx)
        result = self.gdb.remove(idx)

    def test_count_nodes(self):
        # Add a node and see if count is >= 1
        self.test_add_flow()
        assert(self.gdb.count_nodes() >= 1)

    def test_getitem(self):
        # Add a node and see if count is >= 1
        idx = self.test_add_flow()
        assert( self.gdb[idx]["metadata"]["id"] == idx )

'''

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
'''
