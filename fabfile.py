import os
from fabric.api import *

DOCKER_ENV = {
    "NEO4J_DATABASE_DIR" : os.path.join(os.getcwd(), "database/"),
    "NEO4J_PORT"     : 7475,
    "NEO4J_USERNAME" : "buildbot",
    "NEO4J_PASSWORD" : "tulsa",
}

# Export the DOCKER enviorment variables
for key,val in DOCKER_ENV.items():
    os.environ[key] = str(val)

test_directory = "buildbot/test"
test_order = [
    "test_interface.py",
    "test_docker.py",
    "test_graph.py",
    "test_buildbotAPI.py", 
]

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
    cmd = ("docker run "
           "-v {NEO4J_DATABASE_DIR}:/var/lib/neo4j/data "
           "-i -t -d "
           "-e NEO4J_AUTH={NEO4J_USERNAME}:{NEO4J_PASSWORD} "
           "--name buildbot_neo4j "
           "--cap-add=SYS_RESOURCE "
           "-p {NEO4J_PORT}:7474 tpires/neo4j")
        
    local(cmd.format(**os.environ))

def docker_teardown():
    local("docker stop buildbot_neo4j")
    local("docker rm buildbot_neo4j")

def api():
    import time
    local("pkill -9 python")
    local("python REST_API_buildbot.py &")
    time.sleep(1)
    local('''curl -i -H "Content-Type: application/json" -X POST -d '{"description": "unittest", "label": "flow", "status": 0.75, "validation": "unittest", "version": 0.2}' http://localhost:5000/buildbot/api/v1.0/node''')
    
    
def demo():
    local("python demo.py")    
    


