import os
from fabric.api import *

AWS_AMI = {
    "Ubuntu:14.04" : "d05e75b8",
} 

args = {
    "keypair_name"   : "AWS_buildbot",
    "security_group" : "buildbot_instance",
    "instance_type"  : "t2.medium",
    "AWS_AMI" : AWS_AMI["Ubuntu:14.04"],
    "AWS_VPC" : os.environ["AWS_VPC"],
    "AWS_SUBNET" : os.environ["AWS_SUBNET"],
}

# Create AWS key/pair
def create_keypair():
    f_keypair = "{keypair_name}.pem".format(**args)
    if os.path.exists(f_keypair):
        msg = "keypair file already exists! exiting"
        raise ValueError(msg)
    cmd = "ec2-create-keypair {keypair_name} > {keypair_name}.pem"
    local(cmd.format(**args))

def _read_security_group():
    f_group = "{security_group}.group".format(**args)
    
    # Determine the security group
    with open(f_group) as FIN:
        tokens = FIN.read().split()
        args["security_group"] = tokens[1]    

# Create a security group
def create_security_group():
    f_group = "{security_group}.group".format(**args)
    
    if os.path.exists(f_group):
        msg = "group file already exists! exiting"
        raise ValueError(msg)
    
    cmd = (
        'ec2-create-group {security_group} '
        '-d "BuildBot/Dispatch" '
        '--vpc {AWS_VPC} '
        '> '
    )
    local(cmd.format(**args) + f_group)
    _read_security_group()
    
    cmd = "ec2-authorize {security_group} -P 'all' >> "
    local(cmd.format(**args) + f_group)
 
# Launch an instance
def launch_EC2_instance():
    _read_security_group()

    f_instance = "{security_group}.EC2".format(**args)

    if os.path.exists(f_instance):
        msg = "instance file already exists! exiting"
        raise ValueError(msg)
    
    bcmd = (
        "ec2-run-instances ami-{AWS_AMI} "
        "-t {instance_type} "
        "-k {keypair_name} "
        "-g {security_group} "
        "-s {AWS_SUBNET} "
        "--associate-public-ip-address true "
    )

    local(bcmd.format(**args) + " > " + f_instance)
