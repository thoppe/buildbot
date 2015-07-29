import os
import subprocess
from buildbot.graphDB import enhanced_GraphDatabase
from buildbot.utils import neo4j_credentials_from_env

# Test Docker connections by creating a service using them

def test_neo4j_credentials_exist():
    neo4j_credentials_from_env()

def test_neo4j_docker_connection():
    neo4j_login = neo4j_credentials_from_env()
    
    try:
        gdb = enhanced_GraphDatabase(**neo4j_login)
    except:
        subprocess.call(["docker inspect buildbot_neo4j"],
                        shell=True, stderr=subprocess.PIPE)
        raise IOError("docker container likely not found.")

    
