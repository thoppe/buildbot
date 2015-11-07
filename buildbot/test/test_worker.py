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

    
class test_worker_operations(buildbot_worker_test_suite):

    def test_startup_db_from_env(self):
        neo4j_login = neo4j_credentials_from_env()
        self.W.launch_db(**neo4j_login)

    def test_swagger_export(self):
        # Tests if swagger outputs a valid json file
        s = self.W.swagger()
        js = json.loads(str(s))        

    def test_count_nodes_in_db(self):
        # Perform a simple operation on the database.
        self.test_startup_db_from_env()
        self.W._gdb.count_nodes()

    def test_add_node(self):
        # Test adding a node
        self.test_startup_db_from_env()
        self.W.add_node("flow",status=0.75)

    @raises(KeyError)
    def test_add_improper_node_name(self):
        # Try to add a node not defined in the app
        self.test_startup_db_from_env()
        self.W.add_node("UNDEFINED")

    @raises(TraitError)  
    def test_add_improper_node_args(self):
        # Try to add a node not defined in the app
        self.test_startup_db_from_env()
        self.W.add_node("flow",UNDEFINED=2)

        
