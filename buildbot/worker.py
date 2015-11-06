'''
'''
# Main entry point for BuildBot, manages a single instance
from graphDB import enhanced_GraphDatabase

class worker(object):
    '''
    A single instance for BuildBot is a worker. 
    To function, it requires a URI for neo4j and a loaded package file.
    '''
    def __init__(self):
        self.neo4j = {}  # neo4j credentials
        self.gdb = enhanced_GraphDatabase()

    def launch_db(self, **kwargs):
        '''
        Launch the neo4j database connection, requires that
        a username, password and url are passed in.
        '''
        self.neo4j.update(kwargs)

        msg = "{key} not set when launching neo4j"
        for key in ("username","url","password"):
            if key not in self.neo4j:
                raise KeyError(msg.format(key=key))

        self.gdb.launch(**self.neo4j)

    #def load_package(self, 

A = worker()

neo4j_args = {
    "username":"buildbot",
    "password":"tulsa",
    "url":"http://localhost:7474",
}
A.launch_db(**neo4j_args)

#for x in A.gdb:
#    print x

print A.gdb.count_nodes()



#B = worker()
#name = B.load(package_location = "packages/checkin/app.json")
#url = "http://localhost:7474/db/data/"
#B[name].launch(url)
#print B
#print name
#print B[name]

# Code below was ripped out of graphDB
'''
     # from package_manager import buildbot_package      
     # Load the package/schema
        with open(package_location) as FIN:
            raw = FIN.read()
            self.package = buildbot_package(raw)


    def validate_node(self,node):
        #''
        #Returns True only is the input object defined in the package.
        #''
        if node.label not in self.package.nodes:
            msg = "{} object is not a known node-type"
            raise TypeError(msg.format(node))
    
    def validate_relationship(self, rel):
        #''
        #Returns True only is the input object is defined in the package.
        #''
        key = (rel.start, rel.label, rel.end)
        if key not in self.package.relationships:
            msg = "{} object is not a known relationship"
            raise TypeError(msg.format(rel))
'''
