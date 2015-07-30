from neo4jrestclient.client import GraphDatabase, Node
import generic_datatypes

def validate_node(node):
    '''
    Returns True only is the input object is derived from a node_container.
    '''
    if generic_datatypes.node_container not in type(node).mro():
        msg = "{} object is not a known node-type"
        raise TypeError(msg.format(node))

def validate_relationship(rel):
    '''
    Returns True only is the input object is derived from a edge_container.
    '''
    if generic_datatypes.edge_container not in type(rel).mro():
        msg = "{} object is not a known relationship"
        raise TypeError(msg.format(node))

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

    def scalar_query(self, q,returns=[]):
        qval = self.query(q,returns=returns)
        results = qval.elements
        if len(results) != 1:
            msg = "Query {} return {} results, expecting 1"
            raise KeyError(msg.format(q,len(results)))
        
        return qval.elements[0][0]


    def __iter__(self):
        ''' Returns an iterator over flow ID's '''
        q = "START n=node(*) RETURN ID(n)"
        for item in self.query(q):
            yield item[0]

    def iter_over(self, object_name="flow"):
        q = "MATCH (node:{}) RETURN node".format(object_name)
        for item in self.query(q):
            yield item[0]

    def _select_direct_node_from_idx(self, idx):
        q = "MATCH n WHERE ID(n)={} RETURN n".format(idx)
        return self.scalar_query(q,returns=(Node,))

    def __getitem__(self, idx):
        q = "MATCH n WHERE ID(n)={} RETURN n".format(idx)
        try:
            return self.scalar_query(q)
        except KeyError:
            msg = "Node {} not found".format(idx)
            raise KeyError(msg)
        

    def count_nodes(self):
        q = "START n=node(*) return count(n);"
        return self.scalar_query(q)

    def update_node(self, node):
        validate_node(node)
        
        # Make sure node has ID
        if node.id is None:
            msg = "Node must have id before update"
            raise ValueError(msg)
        obj = self.node[node.id]
        
        for key in node:
            val = node[key]
            if obj.get(key) != node[key]:
                obj.set(key, node[key])

        return node

    def add_node(self, node):
        validate_node(node)
        data = dict(**node)

        obj = self.node(**node)
        obj.labels.add(node.label)

        # Set the node.id to the newly created neo4j object id
        node.id = obj.id
        return node

    def add_relationship(self, rel):
        validate_relationship(rel)

        data = dict(**rel)

        start_node = self._select_direct_node_from_idx(rel.start_id)
        end_node   = self._select_direct_node_from_idx(rel.end_id)
        
        obj = start_node.relationships.create(rel.label, end_node, **data)
        rel.id = obj.id

        return rel

    def remove_node(self, idx, stats=True):
        q = '''
        MATCH (n) WHERE
        ID(n)={}
        DELETE n;
        '''.format(idx)

        stats = self.query(q, data_contents=stats).stats
        if not stats["nodes_deleted"]:
            msg = "Nothing matching when node ID {} was deleted."
            raise KeyError(msg.format(idx))

        return stats

    def remove_relationship(self, idx, stats=True):
        q = '''
        MATCH ()-[r]-() WHERE 
        ID(r)={} 
        DELETE r;
        '''.format(idx)

        stats = self.query(q, data_contents=stats).stats
        if not stats["relationship_deleted"]:
            msg = "Nothing matching when relationship ID {} was deleted."
            raise KeyError(msg.format(idx))

        return stats

    #################################################################
    # Not covered by tests yet
    #################################################################
    
    def count_relationships(self):
        q = "START r=rel(*) RETURN COUNT(r);"
        return self.scalar_query(q)
    
    def get_flow_total_time(self, id):
        q = '''
        MATCH p=(start:flow)-[:depends*0..]->(:flow)-[r:requires*0..]->(:job)
        WHERE ID(start)={}
        RETURN SUM( REDUCE(total=0, x in r|total + x.time) )
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
        
