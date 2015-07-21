from nose.tools import *
from unittest import TestCase

from buildbot.neo_flows import enhanced_GraphDatabase
from buildbot.data_schema import defined_relationships
from buildbot.data_schema import defined_nodes

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}

class test_neo4j_graph(TestCase):
    description = "UNITTEST -- delete when complete."
    
    def setUp(self):
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
    
    def tearDown(self):
        q = '''
        MATCH (n)
        WHERE n.description="{}"
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r
        '''.format(self.description)
        
        result = self.gdb.query(q, data_contents=True)
        print result.stats["nodes_deleted"],

    def test_add_flow(self):
        # Create a flow node, return the idx created.
        flow = defined_nodes["flow"]
        node = flow(description=self.description)
        return self.gdb.add_node(node)
    
    def test_remove_node_by_index(self):
        node = self.test_add_flow()
        result = self.gdb.remove_node(node.id)
        assert(result["nodes_deleted"] == 1)
        
    @raises(Exception)
    def test_remove_missing_node(self):
        idx = self.test_add_flow()
        result = self.gdb.remove_node(idx)
        result = self.gdb.remove_node(idx)

    def test_count_nodes(self):
        # Add a node and see if count is >= 1
        self.test_add_flow()
        assert(self.gdb.count_nodes() >= 1)

    def test_getitem(self):
        node = self.test_add_flow()
        idx  = node.id
        assert( self.gdb[idx]["metadata"]["id"] == idx )

    
    def test_add_flow_depends_relationship(self):
        edge_func = defined_relationships[("flow","depends","flow")]

        v1 = self.test_add_flow()
        v2 = self.test_add_flow()
        rel = edge_func(v1,v2)
        return rel

'''
def test_flow_cost_propagation(): pass
'''
