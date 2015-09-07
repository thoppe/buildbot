from nose.tools import *
from unittest import TestCase

from buildbot.graphDB import enhanced_GraphDatabase
from buildbot.utils import neo4j_credentials_from_env

neo4j_login = neo4j_credentials_from_env()
neo4j_login["buildbot_package"] = 'packages/project_management.json'

# Test basic graph operations

class buildbot_test_suite(TestCase):
    test_desc = u"UNITTEST -- delete when complete."
    
    def setUp(self):
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
    
    def tearDown(self):
        q = '''
        MATCH (n)
        WHERE n.description="{}"
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r
        '''.format(self.test_desc)
        
        result = self.gdb.query(q, data_contents=True)
        print result.stats["nodes_deleted"],

class test_basic_graph_operations(buildbot_test_suite):
    
    def test_count_nodes(self):
        # Add a node and see if count is >= 1
        self.test_add_flow()
        assert(self.gdb.count_nodes() >= 1)

    def test_getitem(self):
        node = self.test_add_flow()
        idx  = node.id
        assert( self.gdb[idx]["metadata"]["id"] == idx )
    
    def test_add_flow(self):
        status_level = 0.7
        
        # Create a flow node, return the idx created.
        flow = self.gdb.package.nodes["flow"]
        node = flow(description=self.test_desc,status=status_level)

        # Add to the graph
        node = self.gdb.add_node(node)

        # Make sure an ID has been assigned
        assert(node.id is not None)

        # Make sure data has been copied (check assigned status)
        assert(node.status == status_level)
        
        return node
    
    def test_add_flow_requires_job_relationship(self):
        time_cost = 7.8
        
        # Create the nodes
        v1 = self.gdb.package.nodes["flow"](description=self.test_desc)
        v2 = self.gdb.package.nodes["job"](description=self.test_desc)

        self.gdb.add_node(v1)
        self.gdb.add_node(v2)
        
        edge_func = self.gdb.package.relationships[("flow","requires","job")]
        rel = edge_func(v1,v2,time=time_cost)

        # Add to the graph
        rel = self.gdb.add_relationship(rel)
        
        # Make sure an ID has been assigned
        assert(rel.id is not None)

        # Make sure data has been copied (check assigned status)
        assert(rel['time'] == time_cost)

        return rel
    
    def test_remove_node_by_index(self):
        node = self.test_add_flow()
        stats = self.gdb.remove_node(node.id)
        assert(stats["nodes_deleted"] == 1)

    def test_remove_relationship_by_idx(self):
        rel = self.test_add_flow_requires_job_relationship()
        stats = self.gdb.remove_relationship(rel.id)
        assert(stats["relationship_deleted"] == 1)

    @raises(KeyError)
    def test_remove_missing_node(self):
        idx = self.test_add_flow().id
        self.gdb.remove_node(idx)
        self.gdb.remove_node(idx)

    @raises(KeyError)
    def test_remove_missing_edge(self):
        idx = self.test_add_flow_requires_job_relationship().id
        self.gdb.remove_relationship(idx)
        self.gdb.remove_relationship(idx)

    def test_update_node(self):
        status_level = 0.67
        flow = self.gdb.package.nodes["flow"]
        node = flow(description=self.test_desc,status=status_level)
        obj  = self.gdb.add_node(node)

        # Modify the status and push result
        node["status"] *= 2
        self.gdb.update_node(node)

        obj2 = self.gdb[node.id]
        assert(obj2['data']['status'] == status_level*2)

        
class test_utility_functions(buildbot_test_suite):
    
    def test_time_calculation_proprogation(self):
        # Test if the time calculation proprogates upward to parent flows

        flow = self.gdb.package.nodes["flow"]
        job  = self.gdb.package.nodes["job"]
        depends = self.gdb.package.relationships[("flow","depends","flow")]
        
        f1 = self.gdb.add_node(flow(description=self.test_desc))
        f2 = self.gdb.add_node(flow(description=self.test_desc))
        f3 = self.gdb.add_node(flow(description=self.test_desc))
        f4 = self.gdb.add_node(flow(description=self.test_desc))

        self.gdb.add_relationship(depends(f1,f2))
        self.gdb.add_relationship(depends(f2,f3))
        self.gdb.add_relationship(depends(f3,f4))

        key = ("flow","requires","job")
        job_required = self.gdb.package.relationships[key]
        developer = self.gdb.add_node(job(description=self.test_desc))
        system_admin = self.gdb.add_node(job(description=self.test_desc))
        
        self.gdb.add_relationship(job_required(f3,developer,time=0.5))
        self.gdb.add_relationship(job_required(f2,developer,time=0.1))
        self.gdb.add_relationship(job_required(f4,system_admin,time=0.25))

        assert( self.gdb.get_flow_total_time(f4.id) == 0.25 )
        assert( self.gdb.get_flow_total_time(f3.id) == 0.25+0.5 )
        assert( self.gdb.get_flow_total_time(f2.id) == 0.25+0.5+0.1)
        assert( self.gdb.get_flow_total_time(f1.id) == 0.25+0.5+0.1)
