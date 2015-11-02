# Main entry point for BuildBot, manages a single instance
from graphDB import enhanced_GraphDatabase

class BuildBot(dict):
    '''
    BuildBot is a collection of enhanced_GraphDatabases
    '''
    #def __init__(self):
    #    self.instances = {}

    def load(self, package_location):
        '''
        Load a local package.
        '''
        db = enhanced_GraphDatabase(package_location)
        name = db.package.get_name()
        self[name] = db
        return name


B = BuildBot()
name = B.load(package_location = "packages/checkin/app.json")

url = "http://localhost:7474/db/data/"
B[name].launch(url)

print B
print name
print B[name]
