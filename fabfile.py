import os, time
from fabric.api import *
import fabric.api

# Testing arguments
ENV_VARS = {
    "NEO4J_DATABASE_DIR"  : os.path.join(os.getcwd(), "database/db1"),
    "NEO4J_TCP_ADDR" : "localhost",
    "NEO4J_TCP_PORT" : "7474",
    "NEO4J_AUTH"     : "buildbot:tulsa",
    "BUILDBOT_PORT"  : "5001",
    "buildbot_package" : "packages/checkin/checkin.json",
}

# Split the ENV login keys if this is a local build
a,b = ENV_VARS["NEO4J_AUTH"].split(":")
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
    "test_contracts.py", 
]
test_package_requirements = {
    "test_buildbotAPI.py" : "packages/project_management.json",
    "test_contracts.py"   : "packages/checkin/checkin.json"
}

def test(args = "-x -v"):
    
    nose_cmd = "nosetests-2.7 {args} -s {f_test}"

    for name in test_order:
        f_test = os.path.join(test_directory, name)
        cmd = nose_cmd.format(f_test=f_test,args=args)
        
        if name in test_package_requirements:
            val = test_package_requirements[name]
            os.environ["buildbot_package"] = val
            
        local(cmd)


def clean():
    local("find . -name '*~' | xargs -I {} rm -vf {}")
    local("find . -name '*.pyc' | xargs -I {} rm -vf {}")

def push():
    test(args="")
    local("git status")
    local("git commit -a")
    local("git push")

def commit(): push() # Alias

######################################################################

def package():
    local("python buildbot/package_manager.py")

def metadraw():
    local("python buildbot/utils.py")

######################################################################

def start():
    '''
    Starts a new test instance of NEO4J/BB.
    '''
    with fabric.api.settings(warn_only=True):
        cmd = "python ./dispatch.py --start {buildbot_package} {NEO4J_DATABASE_DIR}"
        local(cmd.format(**ENV_VARS))

def stop():
    '''
    Shutdown all instances of NEO4J.
    '''
    with fabric.api.settings(warn_only=True):
        local("python dispatch.py --shutdown")
    
#def api():
#    local("python buildbot/REST_API_buildbot.py")
    
def demo():
    local("python demo.py")
    #local("python buildbot/package_manager.py")
    #local("python buildbot/interface_package_swagger.py")
    #local("python buildbot/REST_API_buildbot.py")

