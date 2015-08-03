from nose.tools import *
from unittest import TestCase
from buildbot.package_manager import buildbot_package

import buildbot.interface_neo4j_json as interface


class interface_test_suite(TestCase):
    
    def setUp(self):
        # Startup the package manager with the PM package
        f_flows = "packages/project_management.json"
        with open(f_flows) as FIN:
            raw = FIN.read()
        self.package = buildbot_package(raw)

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
