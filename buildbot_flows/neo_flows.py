import neo4jrestclient
from neo4jrestclient.client import GraphDatabase

from data_nodes import flow, validation
_datatype_mapping = {
    "flow"      : flow,
    "validation": validation
}


def wrap_query_type(item):
    (key, val) = item

    if isinstance(val, basestring):
        wrap = '"'
    else:
        wrap = ''
    return '{key}={wrap}{val}{wrap}'.format(key=key, val=val, wrap=wrap)


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

    def get_total_cost(self, id):
        q = '''
        MATCH (start:flow)-[:depends *0..]->(link:flow)
        WHERE ID(start)={}
        RETURN SUM(link.cost)
       '''.format(id)

        return self.scalar_query(q)
    
    def new_flow(self, **kwargs):
        node = self.node(**flow(**kwargs))
        node.labels.add("flow")
        return node

    def new_validation(self, **kwargs):
        node = self.node(**validation(**kwargs))
        node.labels.add("validation")
        return node

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
        
    def export_json(self, idx):
        q = '''
        MATCH (node)
        WHERE ID(node)={}
        RETURN node
        '''.format(idx)
        node = self.scalar_query(q)

        # Idenitify the label type
        labels = set(node["metadata"]["labels"])

        label_id = labels.intersection(_datatype_mapping)

        if len(label_id) > 1:
            raise KeyError("Multiple labels found for idx={}".format(idx))

        obj =  _datatype_mapping[label_id.pop()](**node["data"])

        return obj.json()

        


