'''
Neo4j flows workbench.

In-progress experiment implementing flows as a graph database.


'''

# http://neo4j-rest-client.readthedocs.org/en/latest/info.html
import neo4jrestclient
from neo4jrestclient.client import GraphDatabase, Q

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}

class generic_node_container(object):
    def __init__(self,*args,**kwargs):
        self.data = dict()
        self.data.update(self._object_defaults)
        self.data.update(**kwargs)
        
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, value):
        self.data[key] = value
    def __repr__(self):
        return str(self.data)

    def keys(self):
        return self.data.keys()

    def get_id(self):
        print self

    def __iter__(self):
        for x in self.data:
            yield x
    
class flow(generic_node_container):
    _object_defaults = {
        "cost"    : 0.00,
        "version" : 1.0,
        "author"  : "",
        "owner"   : "",
        "description" : "",
        "fulfillment" : "",
    }


class validation(generic_node_container):
    _object_defaults = {
        "command"  : "",
        "success"  : "",
        "failure"  : "",
    }
    

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
    

if __name__ == "__main__":

    gdb = enhanced_GraphDatabase(**neo4j_login)
    gdb.hard_reset()

    f1 = gdb.new_flow(description = "Install neo4j-rest-client")
    f2 = gdb.new_flow(description = "Install pip")
    f3 = gdb.new_flow(description = "sudo apt-get install pip", cost=0.25)
    f4 = gdb.new_flow(description = "pip install neo4jrestclient", cost=0.10)


    f1.relationships.create("depends", f2)
    f2.relationships.create("depends", f3)
    f1.relationships.create("depends", f4)

    v = gdb.new_validation(
        command="pip --version",
        success="pip 7.0.3 ...",
        failure="command not found",
        )

    f2.relationships.create("validator", v)


    v = gdb.new_validation(
        command='python -c "import neo4jrestclientx"',
        success="",
        failure="ImportError: No module named neo4jrestclientx",
        )

    v.relationships.create("validator", f1)

    for node in gdb.iter_over("flow"):
        idx  = node["metadata"]["id"]
        desc = node["data"]["description"]
        cost = gdb.get_total_cost(idx)
        print "Cost {:0.3f} hrs, Action {}".format(cost, desc)

    msg = "{} known nodes, {} known relationships."
    print msg.format(gdb.count_nodes(), gdb.count_relationships())


