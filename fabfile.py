import os
from fabric.api import *

ENV_VARS = {
    "NEO4J_DATABASE_DIR"  : os.path.join(os.getcwd(), "database/"),
    "NEO4J_PORT_7474_TCP_ADDR" : "localhost",
    "NEO4J_PORT_7474_TCP_PORT" : "7474",
    "NEO4J_ENV_NEO4J_AUTH"     : "buildbot:tulsa",
    "buildbot_package"         : "packages/project_management.json"
}
#ENV_VARS["buildbot_package"] = "packages/checkin/IP_demo.json"

# Split the ENV login keys if this is a local build
a,b = ENV_VARS["NEO4J_ENV_NEO4J_AUTH"].split(":")
ENV_VARS["NEO4J_USERNAME"], ENV_VARS["NEO4J_PASSWORD"] = a,b

# Export the DOCKER enviorment variables (IF NOT SET)
for key,val in ENV_VARS.items():
    if key not in os.environ:
        os.environ[key] = str(val)

test_directory = "buildbot/test"
test_order = [
    "test_interface.py",
    "test_docker.py",
    "test_graph.py",
    "test_buildbotAPI.py", 
]

def test():
    ENV_VARS["buildbot_package"] = "packages/project_management.json"    
    test_str = ' '.join([os.path.join(test_directory,x)
                         for x in test_order])
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

#########################################################################

def package():
    local("python buildbot/package_manager.py")

def metadraw():
    local("python buildbot/utils.py")

#########################################################################

#def docker_build_test_env():
#    docker_neo4j()
#    docker_api()

def neo4j():
    local("docker pull tpires/neo4j")
    
    cmd = ("docker run "
           "-v {NEO4J_DATABASE_DIR}:/var/lib/neo4j/data "
           "-i -t -d "
           "-e NEO4J_AUTH={NEO4J_USERNAME}:{NEO4J_PASSWORD} "
           "--name buildbot_neo4j "
           "--cap-add=SYS_RESOURCE "
           "-p {NEO4J_PORT_7474_TCP_PORT}:7474 "
           "tpires/neo4j")
        
    local(cmd.format(**os.environ))

#def docker_api():
#    local("docker build -t buildbot_api_baseimage .")
#    
#    cmd = ("docker run "
#           "--link buildbot_neo4j:NEO4J "
#           "-i -t -d "
#           "-p 5000:5000 "
#           "--name buildbot_api "
#           "buildbot_api_baseimage "
#           )
#    
#    local(cmd.format(**os.environ))
    
#def docker_teardown_all():
#    docker_teardown_neo4j()
#    docker_teardown_api()
    
def neo4j_teardown():
    try:
        local("docker stop buildbot_neo4j")
        local("docker rm buildbot_neo4j")
    except: pass
        
#def docker_teardown_api():
#    try:
#        local("docker stop buildbot_api")
#        local("docker rm buildbot_api")
#    except: pass
    
def api():
    local("python buildbot/REST_API_buildbot.py")
    
def demo():
    local("python demo.py")
    #local("python buildbot/interface_package_swagger.py")
    #local("python buildbot/REST_API_buildbot.py")

