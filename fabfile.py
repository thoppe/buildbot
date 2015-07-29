import os
from fabric.api import *

test_directory = "buildbot/test"
test_order = [
    "test_interface.py",
    "test_graph.py",
]

docker_args = {
    "local_database_directory" : os.path.join(os.getcwd(), "database/"),
    "neo4j_port": 7475,
    "username": "neo4j",
    "password": "tulsa",
}

def test():
    test_str = ' '.join([os.path.join(test_directory,x) for x in test_order])
    local("nosetests-2.7 -x -s -v {}".format(test_str))

def clean():
    local("find . -name '*~' | xargs -I {} rm -vf {}")
    local("find . -name '*.pyc' | xargs -I {} rm -vf {}")

def push():
    local("nosetests-2.7")
    local("git status")
    local("git commit -a")
    local("git push")

def commit(): push() # Alias

def docker():
    local("docker pull tpires/neo4j")
    cmd = ("docker run  -v {local_database_directory}:/var/lib/neo4j/data -i -t -d -e "
           "NEO4J_AUTH={username}:{password} --name buildbot_neo4j --cap-add=SYS_RESOURCE "
           "-p {neo4j_port}:7474 tpires/neo4j")
    local(cmd.format(**docker_args))
