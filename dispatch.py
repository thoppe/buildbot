#!/usr/bin/python
import argparse, subprocess, json, logging, time
from pprint import pprint

desc = '''Dispatcher for BuildBot'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--list','-l',
                    default=False,
                    action='store_true',
                    help='Returns the running buildbot instances.')

## TO DO: Write a sub-parser for this command
parser.add_argument('--neo4j',
                    nargs='+', default=None,
                    help='Starts/stops neo4j instances (DBlocation/port)',)

## TO DO: Write a sub-parser for this command
parser.add_argument('--buildbot',
                    nargs='+', default=None,
                    help=('Starts/stops buildbot instances '
                          '(package_file/bb port/neo4j port/neo4j db loc)'))

# Starts both a neo4j instance AND a buildbot instance on next port for each
parser.add_argument('--start',
                    nargs=2, default=None,
                    help=('Starts/stops instances '
                          '(package_file/neo4j addr)'))

# Starts both a neo4j instance AND a buildbot instance on next port for each
parser.add_argument('--stopall',
                    default=False, action='store_true',
                    help='Stops all instances!')

args = vars(parser.parse_args())
logging.basicConfig(level=logging.INFO)

_default_location = "database/"

required_containers = [
    'tpires/neo4j',
]

### Verify if Flask exists
import imp
try:
    imp.find_module('flask')
except ImportError:
    logging.error("module flask not found, aborting early")
    exit(2)

def docker_stop_neo4j(**kwargs):
    # Stop the neo4j container running on a specific port

    info = docker_ps()
    
    if kwargs["NEO4J_PORT"] not in list_neo4j_ports():
        print list_neo4j_ports(), kwargs["NEO4J_PORT"]
        msg = 'neo4j port {NEO4J_PORT} not open!'.format(**kwargs)
        logging.critical(msg)
        exit(3)

    kwargs["name"] = "buildbot_neo4j_{NEO4J_PORT}".format(**kwargs)
    msg = "Stopping container {name}"
    logging.info(msg.format(**kwargs))

    cmd = "docker stop {name}".format(**kwargs)
    output = subprocess.check_output(cmd, shell=True)

    cmd = "docker rm {name}".format(**kwargs)
    output = subprocess.check_output(cmd, shell=True)
    

def docker_start_neo4j(**kwargs):
    '''
    Starts a new neo4j instances, returns the generated ID.
    '''
    if kwargs["NEO4J_PORT"] in list_neo4j_ports():
        msg = 'neo4j port {NEO4J_PORT} already in use!'
        logging.critical(msg.format(**kwargs))
        exit(3)
    
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
    #logging.info("Running {}".format(cmd))
    output = subprocess.check_output(cmd, shell=True)
    return output

def docker_pull(name):
    args = {"name": name}
    cmd = 'docker pull {name}'.format(**args)
    output = subprocess.check_output(cmd, shell=True)
    return output

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
    
    output = subprocess.check_output(cmd, shell=True).strip()
    if output:
        NAMES = output.split('\n')
    else:
        NAMES = []

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
            "port"    : data["Config"]["Labels"]["neo4j.port"],
        }
    return rdata


def list_neo4j_ports():
    '''
    Lists all ports used by neo4j docker containers.
    '''
    return [data["port"] for data in
            docker_reduced_ps().values()]

def next_open_neo4j_port():
    starting_port = 7474
    maximum_port  = 2**16
    known_ports = list_neo4j_ports()
    for n in xrange(starting_port, maximum_port):
        port = str(n)
        if port not in known_ports:
            return port
    msg = "Unable to find an open neo4j port"
    logging.error(msg)
    exit(4)
    
####################################################################

def buildbot_start_API(**kwargs):
    # Starts the buildbot API
    bcmd = (
        "python buildbot/REST_API_buildbot.py "
        "--BUILDBOT_PORT {BUILDBOT_PORT} "
        "--NEO4J_AUTH buildbot:tulsa "
        "--NEO4J_TCP_PORT {NEO4J_PORT} "
        "--NEO4J_TCP_ADDR {NEO4J_ADDR} "
        "--buildbot_package {BUILDBOT_PACKAGE} "
    )
    cmd = bcmd.format(**kwargs)
    print cmd
    # Run the process in the background
    subprocess.Popen(cmd, shell=True)
    
    return kwargs["BUILDBOT_PORT"]

def buildbot_stop_API(**kwargs):
    import requests
    url = "http://localhost:{BUILDBOT_PORT}/shutdown"
    r = requests.post(url.format(**kwargs))
    msg = "Stoping buildbot instance on port {BUILDBOT_PORT}"
    logging.info(msg.format(**kwargs))
    return r.text
    
####################################################################


def buildbot_ps():
    # Uses UNIX ps to determine which python Flask were launched and what ports they were mapped to
    
    cmd_args = ['ps', '-aF']
    shell  = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
    output = shell.communicate()[0].strip().split('\n')
    f_buildbot_api = "buildbot/REST_API_buildbot.py"

    data = {}
    for item in output[1:]:  # First row is a header
        if f_buildbot_api not in item:
            continue
        if "python" not in item:
            continue
        item = item.split()
        port = item[item.index("--BUILDBOT_PORT")+1]
        package_name = item[item.index("--buildbot_package")+1]
        data[port] = package_name
    return data

def list_buildbot_ports():
    '''
    Lists all ports used by buildbot Flask apps.
    '''
    return buildbot_ps().keys()

def next_open_buildbot_port():
    starting_port = 5001
    maximum_port  = 7000
    known_ports   = list_buildbot_ports()
    for n in xrange(starting_port, maximum_port):
        port = str(n)
        if port not in known_ports:
            return port
    msg = "Unable to find an open buildbot port"
    logging.error(msg)
    exit(4)
    
#########################################################################

if args["list"]:
    data = {
        "neo4j"    : docker_reduced_ps(),
        "buildbot" : buildbot_ps()
    }
    print json.dumps(data,indent=2)
    exit(0)

if args["stopall"]:

    for port in list_neo4j_ports()[::-1]:
        docker_stop_neo4j(NEO4J_PORT=port,**args)
    for port in list_buildbot_ports()[::-1]:
        buildbot_stop_API(BUILDBOT_PORT=port)
            
    exit(0)

for container_name in required_containers:
    try:
        docker_inspect(container_name)
        #msg = "Found required container {}.".format(container_name)
        #logging.info(msg)
    except subprocess.CalledProcessError:
        msg = "Failed to load container {}.".format(container_name)
        logging.error(msg)
        msg = "Pulling image in 10 seconds if not canceled."
        logging.warning(msg)
        time.sleep(10)
        docker_pull(container_name)

####################################################################

if args["neo4j"] is not None:

    action = args["neo4j"][0].lower()

    if action == "start":
        n_args = len(args["neo4j"])
        if n_args == 1:
            msg = "Location not specified (use only for testing!)"
            logging.warning(msg)
            location = _default_location
            port = next_open_neo4j_port()
        elif n_args == 2:
            port = next_open_neo4j_port()        
        elif n_args == 3:
            action, location, port = args["neo4j"]
        else:
            msg = "--neo4j start location port"
            logging.error(msg)
            exit(2)
        
        ID = docker_start_neo4j(NEO4J_PORT=port,
                                NEO4J_DATABASE_LOCATION=location,
                                **args)
        msg = "Started docker:neo4j {}".format(ID.strip())
        logging.info(msg)
        
    elif action == "stop":
        n_args = len(args["neo4j"])

        n_args_msg = "--neo4j stop port [or 'all']"
        if n_args<2:
            logging.error(n_args_msg)
            exit(2)

        action, port = args["neo4j"][:2]

        try:
            docker_stop_neo4j(NEO4J_PORT=port,**args)
        except:
            if port == "all":
                for n in list_neo4j_ports()[::-1]:
                    docker_stop_neo4j(NEO4J_PORT=n,**args)
            else:
                logging.error(n_args_msg)
                exit(2)
    
    else:
        msg = "Unrecognized neo4j action {}".format(action)
        logging.error(msg)

####################################################################
        
if args["buildbot"] is not None:

    action = args["buildbot"][0].lower()

    if action == "start":
        n_args = len(args["buildbot"])
        
        if n_args == 5:
            action, f_package,port,neo4j_port,neo4j_addr = args["buildbot"]
        else:
            msg = "--buildbot start package_file bb_port neo_port neo_addr"
            logging.error(msg)
            exit(2)
            
        ID = buildbot_start_API(
            NEO4J_PORT=neo4j_port,
            NEO4J_ADDR=neo4j_addr,
            BUILDBOT_PORT=port,
            BUILDBOT_PACKAGE=f_package,
            **args)
        msg = "Started buildbot:{}".format(ID.strip())
        logging.info(msg)


    elif action == "stop":
        n_args = len(args["buildbot"])

        n_args_msg = "--neo4j stop bb_port [or 'all' (not implemented)]"
        if n_args<2:
            logging.error(n_args_msg)
            exit(2)
            
        action, port = args["buildbot"][:2]
        response = buildbot_stop_API(BUILDBOT_PORT=port)
        print response

    else:
        print "UNKNOWN ACTION", action
        exit(3)

####################################################################
        
if args["start"] is not None:

    n_args = len(args["start"])
    f_package,neo4j_db = args["start"]

    neo4j_port = next_open_neo4j_port()
    buildbot_port = next_open_buildbot_port()
    neo4j_addr = "localhost"
    
    ID = docker_start_neo4j(
        NEO4J_PORT=neo4j_port,
        NEO4J_DATABASE_LOCATION=neo4j_db,
        **args)
    
    msg = "Started docker:neo4j {}".format(ID.strip())
    logging.info(msg)
    
    time.sleep(10)
    
    ID = buildbot_start_API(
        NEO4J_PORT=neo4j_port,
        NEO4J_ADDR=neo4j_addr,
        BUILDBOT_PORT=buildbot_port,
        BUILDBOT_PACKAGE=f_package,**args)
    msg = "Started buildbot:{}".format(ID.strip())
    logging.info(msg)
    
