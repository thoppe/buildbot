from fabric.api import run, env, local, sudo

config = {
    "public_DNS"  : "ec2-52-3-179-145.compute-1.amazonaws.com",
    "user"  : "ubuntu",
    "f_pam" : "buildbot_AWS.pem",
}

env.hosts = [config["public_DNS"],]
env.user  = config["user"]
env.key_filename = config["f_pam"]

def ssh():
    cmd = "ssh -i {f_pam} {user}@{public_DNS}"
    local(cmd.format(**config))

def configure():
    #sudo("apt-get update")
    sudo("apt-get install -y git python-pip docker docker.io")
    
    
