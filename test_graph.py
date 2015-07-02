import nose
from nose import with_setup

from buildbot_flows.neo_flows import enhanced_GraphDatabase

neo4j_login = {
    "username" : "neo4j",
    "password" : "tulsa",
    "url" : "http://localhost:7474"
}

gdb = enhanced_GraphDatabase(**neo4j_login)


def setup_func():
    # Create a database structure
    pass

def teardown_func():
    #"tear down test fixtures"
    print "teardown"
    pass

@with_setup(setup_func, teardown_func)
def test1():
    print "FAIL on purpopse.", gdb
    #assert False

@with_setup(setup_func, teardown_func)
def test2():
    pass




if __name__ == "__main__":
    result = nose.run()
