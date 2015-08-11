from fabric.api import run, env, local, sudo, cd

config = {
    "public_DNS"  : "ec2-52-3-179-145.compute-1.amazonaws.com",
    "user"  : "ubuntu",
    "f_pam" : "buildbot_AWS.pem",
    "github_repo" : "https://github.com/tulsa/buildbot",
}

env.hosts = [config["public_DNS"],]
env.user  = config["user"]
env.key_filename = config["f_pam"]

def ssh():
    cmd = "ssh -i {f_pam} {user}@{public_DNS}"
    local(cmd.format(**config))

def configure():
    sudo("apt-get update")
    sudo("apt-get install -y python-dev git python-pip dtach")
    sudo("pip install PyCrypto fabric")


    # Install docker PGP key
    sudo("apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D")
    sudo("echo 'deb https://apt.dockerproject.org/repo ubuntu-trusty main' | sudo tee -a /etc/apt/sources.list")
    
    sudo("apt-get update")
    sudo("apt-get install docker-engine")
    sudo("usermod -a -G docker ubuntu")
    
    run('git clone {github_repo}'.format(**config))
    with cd("buildbot"):
        sudo("pip install -r requirements.txt")
        run('fab docker_neo4j')
    
def api():
    print "Move this to the background"
    with cd("buildbot"):
        run("nohup fab api >& /dev/null < /dev/null &",pty=False)

def view():
    print "View http://{public_DNS}:5000".format(**config)
    
