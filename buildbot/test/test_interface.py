from nose.tools import *
import os
from unittest import TestCase
from buildbot.package import buildbot_package
import buildbot.interface_neo4j_json as interface

from traits.trait_errors import TraitError

_TEST_PACKAGE_LOCATION = "packages/project_management"
_TEST_PACKAGE_NAME =     "app.json"

class interface_test_suite(TestCase):
    
    def setUp(self):
        # Startup the package manager with the PM package
        f_package = os.path.join(_TEST_PACKAGE_LOCATION,
                                 _TEST_PACKAGE_NAME)
        with open(f_package) as FIN:
            raw = FIN.read()

        self.package = buildbot_package()
        self.package.load_package(raw, _TEST_PACKAGE_LOCATION)

        self.flow_data = {
            "version"     : 0.2,
            "description" : u"unittest",
            "validation"  : u"unittest",
            "status"      : 0.75,
            "id" : 7,
        }
        
        self.job_data = {
            "title" : u"Slacker",
            "description" : u"Do nothing all day",
            "id" : 8,
        }
        
        self.requires_data = {
            "time" : 3.7,
            "id": 22,
        }


class test_package_interface(interface_test_suite):
    
    def test_node_json(self):
        P = self.package
        node1     = P.nodes["flow"](**self.flow_data)
        json_text = node1.json()
        node2     = interface.convert_json2node_container(json_text,P)
        assert(node1 == node2)
        assert( node1.id == node2.id )

    def test_relationship_json(self):
        P = self.package

        node1 = P.nodes["flow"](**self.flow_data)
        node2 = P.nodes["job"] (**self.job_data)
        requires = P.relationships[("flow","requires","job")]
        edge1 = requires(node1,node2,**self.requires_data)
        json_text = edge1.json()
        edge2 = interface.convert_json2edge_container(json_text,P)

        assert( edge1 == edge2 )
        assert( edge1.id == edge2.id )
        
    def test_schema_org(self):
        print "SCHEMA.ORG TEST SKIPPED FOR NOW\n"
        return True
        node = self.package.nodes["person"]()
        ''' 
        This is only defined in schema.org and should 
        fail if not read properly '''
        node["url"] = u"localhost"

    @raises(TraitError)
    def test_missing_key(self):
        node = self.package.nodes["person"]
        node(not_a_real_field="blank")        
