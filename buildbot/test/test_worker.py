from nose.tools import *
from unittest import TestCase
import os, json

from traits.trait_errors import TraitError
from buildbot.utils import neo4j_credentials_from_env
from buildbot.worker import worker

_TEST_PACKAGE = "packages/project_management/app.json"

# Test basic graph operations
class buildbot_worker_test_suite(TestCase):

    def setUp(self):

        self.W = worker()
        self.W.load_package(location=_TEST_PACKAGE)

        neo4j_login = neo4j_credentials_from_env()
        self.W.launch_db(**neo4j_login)

    
class test_worker_operations(buildbot_worker_test_suite):

    def test_swagger_export(self):
        # Tests if swagger outputs a valid json file
        s = self.W.swagger()
        js = json.loads(str(s))        

    def test_count_nodes_in_db(self):
        # Perform a simple operation on the database.
        self.W._gdb.count_nodes()

    def test_add_node(self):
        # Test adding a node
        self.W.add_node("flow",status=0.75)

    @raises(KeyError)
    def test_add_improper_node_name(self):
        # Try to add a node not defined in the app
        self.W.add_node("UNDEFINED")

    @raises(TraitError)  
    def test_add_improper_node_args(self):
        # Try to add a node not defined in the app
        self.W.add_node("flow",UNDEFINED=2)

    def test_get_node(self):
        # Test getting a newly added node
        node1 = self.W.add_node("flow", status=0.6)
        node2 = self.W.get_node(node1.id)
        assert( node1["status"] == node2["status"] )

    @raises(KeyError)
    def test_get_missing_node(self):
        # Raise an error if node_id is not found
        self.W.get_node(-1)
    
    def test_remove_node(self):
        # Test removing a newly added node
        node1 = self.W.add_node("flow", status=0.6)
        self.W.remove_node(node1.id)
        
    @raises(KeyError)
    def test_remove_missing_node(self):
        # Test removing a newly added node
        self.W.remove_node(-1)

    def test_update_node(self):
        val = 0.2
        node1 = self.W.add_node("flow", status=val)

        # Modify the status and push result
        node1["status"] *= 2
        
        node2 = self.W.update_node(node1.id, **node1)
        assert(node2["status"] == val*2)
