import neo4jrestclient
from neo4jrestclient.client import GraphDatabase

from flow_datatypes import *

class enhanced_GraphDatabase(GraphDatabase):

    def scalar_query(self, q):
        return iter(self.query(q)).next()[0]

    def count_nodes(self):
        q = "START n=node(*) return count(n);"
        return self.scalar_query(q)

    def count_relationships(self):
        q = "START r=rel(*) return count(r);"
        return self.scalar_query(q)

    def hard_reset(self):
        q = '''
        MATCH (n)
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r;
        '''
        return self.query(q)

    def new(self,**node_properties):
        node = self.node(**node_properties)        
        return node

    def new_flow(self, **kwargs):
        node = self.node(**flow(**kwargs))
        node.labels.add("flow")
        return node

    def new_validation(self, **kwargs):
        node = self.node(**validation(**kwargs))
        node.labels.add("validation")
        return node

    def __iter__(self):
        ''' Returns an iterator over flow ID's '''
        q = "START n=node(*) RETURN ID(n)"
        for item in self.query(q):
            yield item[0]

    def iter_over(self, object_name="flow"):
        q = "MATCH (node:{}) RETURN node".format(object_name)
        for item in self.query(q):
            yield item[0]

    def __getitem__(self, idx):
        q = "MATCH n WHERE ID(n)={} RETURN n".format(idx)
        return self.scalar_query(q)

    def scalar_query(self, q):
        return iter(self.query(q)).next()[0]

    def count_nodes(self):
        q = "START n=node(*) return count(n);"
        return self.scalar_query(q)

    def count_relationships(self):
        q = "START r=rel(*) return count(r);"
        return self.scalar_query(q)

    def hard_reset(self):
        q = '''
        MATCH (n)
        OPTIONAL MATCH (n)-[r]-()
        DELETE n,r
        '''
        return self.query(q)

    def new(self,**node_properties):
        node = self.node(**node_properties)        
        return node

    def new_flow(self, **kwargs):
        node = self.node(**flow(**kwargs))
        node.labels.add("flow")
        return node

    def new_validation(self, **kwargs):
        node = self.node(**validation(**kwargs))
        node.labels.add("validation")
        return node

    def get_total_cost(self, id):
        q = '''
        MATCH (start:flow)-[:depends *0..]->(link:flow)
        WHERE ID(start)={}
        RETURN SUM(link.cost)
       '''.format(id)

        return self.scalar_query(q)
    
