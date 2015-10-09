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
    

def docker_start_neo4j(**kwargs):
    '''
    Starts a new neo4j instances, returns the generated ID.
    '''
    
    kwargs["USERNAME"] = "buildbot"
    kwargs["PASSWORD"] = "tulsa"
    kwargs["container_name"] = "buildbot_neo4j_{NEO4J_PORT}".format(**kwargs)
        
    bcmd = (
        "docker run "
        "-v {NEO4J_DATABASE_LOCATION}:/var/lib/neo4j/data "
        "-i -t -d "
        "-e NEO4J_AUTH={USERNAME}:{PASSWORD} "
        "--name {container_name} "
        "--label neo4j.port={NEO4J_PORT} "
        "--label neo4j=1 "
        "--cap-add=SYS_RESOURCE "
        "-p {NEO4J_PORT}:7474 "
        "tpires/neo4j"
    )
    cmd = bcmd.format(**kwargs)
    logging.info("Running {}".format(cmd))
    output = subprocess.check_output(cmd, shell=True)
    return output

def docker_pull(name):
    args = {"name": name}
    cmd = 'docker pull {name}'.format(**args)
    output = subprocess.call(cmd, shell=True)

def docker_inspect(name):
    args = {"name": name}
    cmd = 'docker inspect {name}'.format(**args)
    output = subprocess.check_output(cmd, shell=True)
    return json.loads(output)

def docker_ps(show_all=True):
    '''
    Runs inpsect on all neo4j instances and returns a dict
    mapping names to dictionary of docker inspect.
    '''

    args = {
        "images" : "",
        "format" : '{{.ID}}',
    }

    # Show images instead of containers
    if show_all:
        args["show_all"] = '-a'
    
    # Search only for containers with neo4j label
    cmd = 'docker ps {show_all} --format {format} --filter "label=neo4j=1"'
    cmd = cmd.format(**args)
    
    output = subprocess.check_output(cmd, shell=True)
    NAMES  = output.strip().split('\n')

    data = {}
    for name in NAMES:
        cmd = 'docker inspect {}'.format(name)
        output = subprocess.check_output(cmd, shell=True)
        js = json.loads(output)[0]
        data[js["Name"]] = js

    return data

def docker_reduced_ps():
    rdata = {}
    for name,data in docker_ps().items():
        rdata[name] = {
            "name"    : name,
            "created" : data["Created"],
            "running" : data["State"]["Running"],
            "port"    : int(data["Config"]["Labels"]["neo4j.port"]),
        }
    return rdata

if args["list"]:

    print "** Running Containers **"
    data = docker_reduced_ps()
    for key,val in data.items():
        pprint(val)

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
        ID = docker_start_neo4j(NEO4J_PORT=port,
                                NEO4J_DATABASE_LOCATION=location,
                                **args)
        msg = "Started docker:neo4j {}".format(ID)
        logging.info(msg)
        
    elif action == "stop":
        if len(args["neo4j"])<2:
            msg = "--neo4j stop port"
            logging.error(msg)
            exit(2)
        action, port = args["neo4j"][:2]
        docker_stop_neo4j(NEO4J_PORT=port,**args)
    
    else:
        msg = "Unrecognized neo4j action {}".format(action)
        logging.error(msg)




