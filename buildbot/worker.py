import os
from graphDB import enhanced_GraphDatabase
from package import buildbot_package

class worker(object):
    '''
    A single instance for BuildBot is a worker. 
    To function, it requires a URI for neo4j and a loaded package file.
    '''
    def __init__(self):
        self.neo4j = {}  # neo4j credentials
        self.package_args = {}
        
        self._gdb  = enhanced_GraphDatabase()
        self._pack = buildbot_package()

        self.nodes, self.relationships = None, None

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

        self._gdb.launch(**self.neo4j)

    def load_package(self, **kwargs):
        '''
        Load, from disk, a buildbot package, requires that
        'location' has been set.
        '''
        self.package_args.update(kwargs)
        
        msg = "{key} not set when launching package"
        for key in ("location",):
            if key not in self.package_args:
                raise KeyError(msg.format(key=key))

        loc = self.package_args["location"]

        # Set the package location
        self.package_args["local_dir"] = os.path.dirname(os.path.realpath(loc))

        # Check if the file exists
        if not os.path.exists(loc):
            msg = "Package file {} not found."
            raise OSError(msg.format(loc))
        
        # Load the file from disk
        with open(loc) as FIN:
            self.package_args["text"] = FIN.read()

        self._pack.load_package(**self.package_args)

        # Expose the nodes and edges
        self.nodes = self._pack.nodes
        self.relationsips = self._pack.relationships

    def swagger(self):
        '''
        Returns the loaded package swagger file.
        '''
        return self._pack.export()

    def add_node(self, name, **kwargs):
        '''
        Adds a node and validates that it is proper.
        '''
        obj  = self.nodes[name](**kwargs)
        node = self._gdb.add_node(obj)
        return node
        #print type(node)
        #print type(node)
        # Add to the graph
        #node = self.gdb.add_node(node)


if __name__ == "__main__":

    A = worker()

    package_args = {
        'location' : "../packages/checkin/app.json"
    }
    A.load_package(**package_args)

    neo4j_args = {
        "username":"buildbot",
        "password":"tulsa",
        "url":"http://localhost:7474",
    }

    A.launch_db(**neo4j_args)
    print "known nodes", A.gdb.count_nodes()
    print "length of package", len(str(A._pack))
    print "length of swagger file",len(str(A.swagger()))

    print A.nodes
    A.add_node('ping', timestamp=20)

