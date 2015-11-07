from nose.tools import *
from unittest import TestCase
import os, json

from buildbot.utils import neo4j_credentials_from_env
#from buildbot.graphDB import enhanced_GraphDatabase
#from buildbot.package import buildbot_package
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

    def test_package_length(self):
        # Check that the package length is non-zero (quick check if loaded)
        assert( str(self.W.pack) )

    def test_count_nodes_in_db(self):
        # Perform an operation on the database
        self.test_startup_db_from_env()
        self.W.gdb.count_nodes()
