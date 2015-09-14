from nose.tools import *
from unittest import TestCase

import os, json
from buildbot.graphDB import enhanced_GraphDatabase

from buildbot.utils import neo4j_credentials_from_env
neo4j_login = neo4j_credentials_from_env()

#from buildbot.REST_API_buildbot import API
#API.config["DEBUG"] = True

class buildbotAPI_test_suite(TestCase):

    def setUp(self):
        neo4j_login["buildbot_package"]= "packages/checkin/checkin.json"
        self.gdb = enhanced_GraphDatabase(**neo4j_login)
        self.func = self.gdb.package.actions["pingme"]
    
    def tearDown(self):
        pass
        
    def pingme_test(self):
        # Simple tests makes sure we load the package actions
        func = self.gdb.package.actions["pingme"]
        func(name="travis")
