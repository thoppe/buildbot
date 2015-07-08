import neo4jrestclient
from neo4jrestclient.client import GraphDatabase

from data_nodes import flow, validation
import generic_datatypes

def validate_node(node):
    '''
    Returns True only is the input object is derived from a node_container.
    '''
    return generic_datatypes.node_container in type(node).mro()

def wrap_query_type(item):
    (key, val) = item

    if isinstance(val, basestring):
        wrap = '"'
    else:
        wrap = ''
    return '{key}={wrap}{val}{wrap}'.format(key=key, val=val, wrap=wrap)

def hard_reset(gdb):
    q = '''
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-()
    DELETE n,r;
    '''
    return gdb.query(q)


class enhanced_GraphDatabase(GraphDatabase):

    def scalar_query(self, q):
        return iter(self.query(q)).next()[0]

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

    def count_nodes(self):
        q = "START n=node(*) return count(n);"
        return self.scalar_query(q)

    def add(self, node):
        if not validate_node(node):
            msg = "{} object is not a known node-type"
            raise TypeError(msg.format(node))
        
        data = dict(**node)

        obj = self.node(**node)
        obj.labels.add(node.label)
        return obj.id

    def remove(self, idx, stats=True):
        q = '''
        START n=node({})
        OPTIONAL MATCH n-[r]-()
        DELETE r, n;
        '''.format(idx)

        result = self.query(q, data_contents=stats)
        return result.stats


    #################################################################
    # Not covered by tests yet
    #################################################################
    
    def count_relationships(self):
        q = "START r=rel(*) return count(r);"
        return self.scalar_query(q)

    def get_total_cost(self, id):
        q = '''
        MATCH (start:flow)-[:depends *0..]->(link:flow)
        WHERE ID(start)={}
        RETURN SUM(link.cost)
       '''.format(id)

        return self.scalar_query(q)

    def select(self, label, **kwargs):
        q = '''
        MATCH (node:{label})
        WHERE
        {where}
        RETURN ID(node)
        '''
        key_pairs = ['node.{}'.format(wrap_query_type(x))
                     for x in kwargs.items()]
        
        where_string = ' AND '.join(key_pairs)
        q = q.format(label=label, where=where_string)
        print q
        return self.scalar_query(q)
        
