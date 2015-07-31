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
    test_desc = "UNITTEST -- delete when complete."

    flow_data1 = {"description": "unittest", "label": "flow",
                  "status": 0.75, "validation": "unittest", "version": 0.2}
    
    def setUp(self):
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
        self.app = API.test_client()
    
    def tearDown(self):
        q = '''
        MATCH (n)
        WHERE n.description="{}"
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r
        '''.format(self.test_desc)
        
        result = self.gdb.query(q, data_contents=True)
        print result.stats["nodes_deleted"],

class test_basic_API_operations(buildbotAPI_test_suite):

    def test_create_flow_node(self):
        json_string = json.dumps(self.flow_data1)
        response = self.app.post('/buildbot/api/v1.0/node/create',
                                 data=json_string,
                                 content_type='application/json')
        return response.data

    def test_get_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1)
        url = '/buildbot/api/v1.0/node/{}'.format(node1.id)
        response = self.app.get(url)
        node2 = interface.convert_json2node_container(response.data)
        
        # Check that they match
        assert( node1 == node2 )

    def test_remove_node(self):
        js_node1 = self.test_create_flow_node()
        node1 = interface.convert_json2node_container(js_node1)
        url = '/buildbot/api/v1.0/node/remove/{}'.format(node1.id)
        response = self.app.post(url)
