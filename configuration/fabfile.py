import os
from fabric.api import *

args = {
    "keypair_name"   : "AWS_buildbot",
    "security_group" : "buildbot_instance"
}

# Create AWS key/pair
def create_keypair():
    f_keypair = "{keypair_name}.pem".format(**args)
    if os.path.exists(f_keypair):
        msg = "keypair file already exists! exiting"
        raise ValueError(msg)
    cmd = "ec2-create-keypair {keypair_name} > {keypair_name}.pem"
    local(cmd.format(**args))

# Create a security group
def create_security_group():
    f_group = "{security_group}.group".format(**args)
    
    if os.path.exists(f_group):
        msg = "group file already exists! exiting"
        raise ValueError(msg)
    cmd = 'ec2-create-group {security_group} -d "BuildBot/Dispatch" > '
    local(cmd.format(**args) + f_group)
    
    cmd = "ec2-authorize {security_group} -p 22 -s 203.0.113.25/32 >> "
    local(cmd.format(**args) + f_group)
 
