from nose.tools import *
from unittest import TestCase

import os, json
from buildbot.graphDB import enhanced_GraphDatabase

# Helper functions
import buildbot.interface_neo4j_json as interface

from buildbot.utils import neo4j_credentials_from_env

from buildbot.REST_API_buildbot import API
API.config["DEBUG"] = True

# Test basic graph operations
class buildbotAPI_test_suite(TestCase):
    test_desc = "unittest"

    def setUp(self):
        neo4j_login = neo4j_credentials_from_env()
        neo4j_login["buildbot_package"]= "packages/project_management.json"
        
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
        self.P   = self.gdb.package
        self.API = API.test_client()
        self.flow_data1 = {"description": self.test_desc,
                           "label": "flow",
                           "status": 0.75,
                           "validation": "unittest",
                           "version": 0.2}
        
    def tearDown(self):
        q = '''
        MATCH (n)
        WHERE n.description="{}"
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r
        '''.format(self.test_desc)
        
        result = self.gdb.query(q, data_contents=True)
        print result.stats["nodes_deleted"],

    def post(self, url, data={}):
        url = url.format(**data)
        json_string = json.dumps(data)
        return self.API.post(url, data=json_string,
                             content_type='application/json')

    def delete(self, url, data={}):
        url = url.format(**data)
        json_string = json.dumps(data)
        return self.API.delete(url, data=json_string,
                               content_type='application/json')        

    def get(self, url, data={}):
        url = url.format(**data)
        js  = json.dumps(data)
        return self.API.get(url,data=js,
                            content_type='application/json')

class test_basic_API_operations(buildbotAPI_test_suite):

    def test_create_flow_node(self):
        response = self.post('/buildbot/api/v1.0/node/{label}/create',
                             self.flow_data1)
        return response.data

    def test_search_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1,self.P)
        search_query = node1.dict()
        search_query.pop("id")
        
        response = self.get('/buildbot/api/v1.0/node/{label}/search',
                            search_query)
        match_idx = json.loads(response.data)
        assert(node1.id in match_idx["match_nodes"])
        return match_idx["match_nodes"]

    def test_get_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1,self.P)
        url = '/buildbot/api/v1.0/node/{label}/{id}'
        response = self.get(url, node1.dict())
        node2 = interface.convert_json2node_container(response.data,self.P)
        
        # Check that they match
        assert( node1 == node2 )

    def test_remove_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1,self.P)
        url = '/buildbot/api/v1.0/node/{label}/remove'
        response = self.delete(url,node1.dict())
        stats = json.loads(response.data)
        assert(stats["nodes_deleted"]==1)

    def test_remove_relationship(self):
        json_rel_string = self.test_create_relationship()
        rel = interface.convert_json2edge_container(json_rel_string,self.P)
        
        rel_data = {
            "id":rel.id,
            "start":rel.start,
            "end":rel.end,
            "label":rel.label,
        }
        url = '/buildbot/api/v1.0/relationship/{start}/{label}/{end}/remove'
        response = self.delete(url,rel_data)

        stats = json.loads(response.data)
        assert(stats["relationship_deleted"]==1)
        return response.data

    def test_create_relationship(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1,self.P)

        js_node1 = self.test_create_flow_node()
        node2 = interface.convert_json2node_container(js_node1,self.P)

        rel_data = {
            "start_id":node1.id,
            "end_id"  :node2.id,
            "label":"depends",
            "start":node1.label,
            "end":node2.label,
        }
        url = '/buildbot/api/v1.0/relationship/{start}/{label}/{end}/create'
        
        response = self.post(url,data=rel_data)
        return response.data

    def test_update_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1,self.P)
        
        # Change the status
        node1["status"] *= 2
        json_string2 = node1.json()
        
        response = self.post('/buildbot/api/v1.0/node/{label}/update',
                             node1.dict())
        node2 = interface.convert_json2node_container(response.data,self.P)

        # Check that the returned node is updated
        assert(node1 == node2)
