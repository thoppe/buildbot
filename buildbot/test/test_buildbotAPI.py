from nose.tools import *
from unittest import TestCase

import os, json
from buildbot.graphDB import enhanced_GraphDatabase
from buildbot.data_schema import defined_relationships
from buildbot.data_schema import defined_nodes
import buildbot.interface_neo4j_json as interface

from buildbot.utils import neo4j_credentials_from_env
neo4j_login = neo4j_credentials_from_env()

from buildbot.REST_API_buildbot import API
API.config["DEBUG"] = True

# Test basic graph operations
class buildbotAPI_test_suite(TestCase):
    test_desc = "unittest"

    def setUp(self):
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
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
        return self.API.post(url, data=data, content_type='application/json')

    def get(self, url):
        return self.API.get(url)

class test_basic_API_operations(buildbotAPI_test_suite):

    def test_create_flow_node(self):
        json_string = json.dumps(self.flow_data1)
        response = self.post('/buildbot/api/v1.0/node/create',json_string)
        return response.data

    def test_get_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1)
        url = '/buildbot/api/v1.0/node/{}'.format(node1.id)
        response = self.get(url)
        node2 = interface.convert_json2node_container(response.data)
        
        # Check that they match
        assert( node1 == node2 )

    def test_remove_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1)
        url = '/buildbot/api/v1.0/node/remove/{}'.format(node1.id)
        response = self.post(url)
        stats = json.loads(response.data)
        assert(stats["nodes_deleted"]==1)

    def test_remove_relationship(self):
        json_rel_string = self.test_create_relationship()
        rel = interface.convert_json2edge_container(json_rel_string)
        url = '/buildbot/api/v1.0/relationship/remove/{}'.format(rel.id)
        response = self.post(url)
        stats = json.loads(response.data)
        assert(stats["relationship_deleted"]==1)
        return response.data

    def test_create_relationship(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1)

        js_node1 = self.test_create_flow_node()
        node2 = interface.convert_json2node_container(js_node1)

        rel_data = {"label":"depends",
                    "start_id":node1.id,
                    "end_id"  :node2.id}

        json_rel_string = json.dumps(rel_data)
        response = self.post('/buildbot/api/v1.0/relationship/create',
                             data=json_rel_string,)
        return response.data

    def test_update_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1)
        
        # Change the status
        node1["status"] *= 2
        json_string2 = interface.convert_node_container2json(node1)
        response = self.post('/buildbot/api/v1.0/node/update',
                             data=json_string2)
        node2 = interface.convert_json2node_container(response.data)

        # Check that the returned node is updated
        assert(node1 == node2)
