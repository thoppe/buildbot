import os
from fabric.api import *

args = {
    "keypair_name" : "AWS_buildbot",
}

# Create AWS key/pair
def create_keypair():
    f_keypair = "{keypair_name}.pem".format(**args)
    if os.path.exists(f_keypair):
        msg = "keypair file already exists! exiting"
        raise ValueError(msg)
    cmd = "ec2-create-keypair {keypair_name} > {keypair_name}.pem"
    local(cmd.format(**args))
