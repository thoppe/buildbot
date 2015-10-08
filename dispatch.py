#!/usr/bin/python
import argparse, subprocess, json, logging, time
from pprint import pprint

desc = '''Dispatcher for BuildBot'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--list','-l',
                    default=False,
                    action='store_true',
                    help='Returns the running buildbot instances.')
parser.add_argument('--neo4j',
                    nargs='+', default=None,
                    help='Starts a neo4j instance (port/location)',)

args = vars(parser.parse_args())

logging.basicConfig(level=logging.INFO)

required_containers = [
    'tpires/neo4j',
]

def docker_stop_neo4j(**kwargs):
    # Find all running containers, and match with one that
    stop_ID = None
    
    data = docker_ps()
    for item in data:
        status = item["Status"].split('->')[0].strip()
        if len(status.split(':')) == 2:
            port = status.split(':')
        print status, port
            
    print data
    
    print "HERE!"
    exit()
    

def docker_launch_neo4j(**kwargs):
    kwargs["USERNAME"] = "buildbot"
    kwargs["PASSWORD"] = "tulsa"
    kwargs["container_name"] = "buildbot_neo4j_{NEO4J_PORT}".format(**kwargs)
        
    bcmd = (
        "docker run "
        "-v {NEO4J_DATABASE_LOCATION}:/var/lib/neo4j/data "
        "-i -t -d "
        "--rm "
        "-e NEO4J_AUTH={USERNAME}:{PASSWORD} "
        "--name {container_name} "
        "--cap-add=SYS_RESOURCE "
        "-p {NEO4J_PORT}:7474 "
        "tpires/neo4j"
    )
    cmd = bcmd.format(**kwargs)
    logging.info("Running {}".format(cmd))
    output = subprocess.call(cmd, shell=True)
    print "OUTPUET!", output

def docker_pull(name):
    args = {"name": name}
    cmd = 'docker pull {name}'.format(**args)
    output = subprocess.call(cmd, shell=True)

def docker_inspect(name):
    args = {"name": name}
    cmd = 'docker inspect {name}'.format(**args)
    output = subprocess.check_output(cmd, shell=True)
    return json.loads(output)

def docker_ps(images=False):
    '''
    Returns a list of dictionaries describing
    the open BuildBot instances.
    '''
    names = ["ID", "Image", "Command", "CreatedAt",
             "RunningFor","Ports", "Status", "Size", "Labels"]

    args = {
        "images" : "",
        "format" : ','.join(["{{.%s}}"%x for x in names])
    }

    # Show images instead of containers
    if images:
        args["images"] = '-a'
        
    cmd = 'docker ps {images} --format {format}'.format(**args)
    output = subprocess.check_output(cmd, shell=True)

    data   = [dict(zip(names, line.split(',')))
              for line in output.strip().split('\n')
              if line]
    return data


if args["list"]:

    print "** Running Containers **"
    data = docker_ps()
    print data

    print "** Running Images **"
    data = docker_ps(images=True)
    print data
    exit(0)


for container_name in required_containers:
    try:
        docker_inspect(container_name)
        msg = "Found required container {}.".format(container_name)
        logging.info(msg)
    except subprocess.CalledProcessError:
        msg = "Failed to load container {}.".format(container_name)
        logging.error(msg)
        msg = "Pulling image in 10 seconds if not canceled."
        logging.warning(msg)
        time.sleep(10)
        docker_pull(container_name)


if args["neo4j"] is not None:

    action = args["neo4j"][0].lower()

    if action == "start":
        if len(args["neo4j"])!=3:
            msg = "--neo4j start port location"
            logging.error(msg)
            exit(2)
            
        action, port, location = args["neo4j"]
        docker_launch_neo4j(NEO4J_PORT=port,
                            NEO4J_DATABASE_LOCATION=location,
                            **args)
        
    if action == "stop":
        if len(args["neo4j"])<2:
            msg = "--neo4j stop port"
            logging.error(msg)
            exit(2)
        action, port = args["neo4j"][:2]
        docker_stop_neo4j(NEO4J_PORT=port,**args)
    
    else:
        msg = "Unrecgonized neo4j action {}".format(action)
        logging.error(msg)




