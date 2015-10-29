#!/usr/bin/env python

import argparse, subprocess, json, logging, time, os, shlex
import requests

desc = '''Dispatcher for BuildBot'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--list','-l',
                    default=False,
                    action='store_true',
                    help='Returns the running buildbot instances.')

# Starts both a neo4j instance AND a buildbot instance on next port for each
parser.add_argument('--start',
                    nargs=2, default=None,
                    help=('Starts instances '
                          '(package_file/neo4j addr)'))

# Starts both a neo4j instance AND a buildbot instance on next port for each
parser.add_argument('--shutdown',
                    default=False, action='store_true',
                    help='Stops all instances!')

_WSGI_HEADER = "wsgi:gunicorn_load"

'''
# These commands are depreciated
## TO DO: Write a sub-parser for this command
parser.add_argument('--neo4j',
                    nargs='+', default=None,
                    help='Starts/stops neo4j instances (DBlocation/port)',)

## TO DO: Write a sub-parser for this command
parser.add_argument('--buildbot',
                    nargs='+', default=None,
                    help=('Starts/stops buildbot instances '
                          '(package_file/bb port/neo4j port/neo4j db loc)'))
'''

args = vars(parser.parse_args())
logging.basicConfig(level=logging.INFO)

_default_location = "database/"

_required_containers = [
    'tpires/neo4j',
]

# Requests module is very chatty, turn off the logging level for info
logging.getLogger("requests").setLevel(logging.WARNING)


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
        msg = 'neo4j port {NEO4J_PORT} not open!'.format(**kwargs)
        logging.critical(msg)
        exit(3)

    kwargs["name"] = "buildbot_neo4j_{NEO4J_PORT}".format(**kwargs)
    msg = "Stopping container {name}"
    logging.info(msg.format(**kwargs))

    cmd = "docker stop {name}".format(**kwargs)
    output = subprocess.check_output(cmd.split())

    cmd = "docker rm {name}".format(**kwargs)
    output = subprocess.check_output(cmd.split())
    

def docker_start_neo4j(**kwargs):
    '''
    Starts a new neo4j instances, returns the generated ID.
    '''
    if kwargs["NEO4J_PORT"] in list_neo4j_ports():
        msg = 'neo4j port {NEO4J_PORT} already in use!'
        logging.critical(msg.format(**kwargs))
        exit(3)

    # Create the database location if it doesn't exist
    f_db = kwargs["NEO4J_DATABASE_LOCATION"]
    if not os.path.exists(f_db):
        msg = "neo4j database location {NEO4J_DATABASE_LOCATION} doesn't exist. Creating."
        logging.warning(msg.format(**kwargs))
        os.system('mkdir -p '+f_db)
    
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
    output = subprocess.check_output(cmd.split())
    return output

def docker_pull(name):
    args = {"name": name}
    cmd = 'docker pull {name}'.format(**args)
    output = subprocess.check_output(cmd.split())
    return output

def docker_inspect(name):
    args = {"name": name}
    cmd = 'docker inspect {name}'.format(**args)
    output = subprocess.check_output(cmd.split())
    return json.loads(output)

def docker_ps(show_all=True):
    '''
    [BLOCKING]
    Runs inspect on all neo4j instances and returns a dict
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
    output = subprocess.check_output(cmd.split()).strip()

    if output:
        NAMES = output.split('\n')
    else:
        NAMES = []

    data = {}
    for name in NAMES:
        cmd = 'docker inspect {}'.format(name)
        output = subprocess.check_output(cmd.split())
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

def status_local_neo4j(**kwargs):
    url = "http://{NEO4J_ADDR}:{NEO4J_PORT}".format(**kwargs)
    r = requests.get(url)
    return r.status_code == 200


def wait_until_neo4j_is_up(attempts=50,**kwargs):
    attempt_count = 0
    while True:
        attempt_count += 1
        try:
            if status_local_neo4j(**kwargs):
                break
        except requests.exceptions.ConnectionError:
            msg = "Waiting to establish neo4j connection {}"
            logging.info(msg.format(attempt_count))
            pass
        if attempt_count > attempts:
            logging.critical("Could not establish neo4j connection")
            exit()
        time.sleep(0.5)

    
####################################################################

def buildbot_start_API(**kwargs):
    # Starts the buildbot API
    #cmd_args = 'gunicorn wsgi:app --bind 0.0.0.0:{}'
    #cmd_args = cmd_args.format(next_open_buildbot_port())

    #"./buildbot/REST_API_buildbot.py "
    
    API_args = (
        "--BUILDBOT_PORT {BUILDBOT_PORT} "
        "--NEO4J_AUTH buildbot:tulsa "
        "--NEO4J_TCP_PORT {NEO4J_PORT} "
        "--NEO4J_TCP_ADDR {NEO4J_ADDR} "
        "--buildbot_package {BUILDBOT_PACKAGE} "
    )
    API_args = API_args.format(**kwargs)
    cmd = '''gunicorn '{}("{}")' '''.format(_WSGI_HEADER,API_args)
    print API_args
    print cmd
    exit()
    

    # Run the process in the background
    subprocess.Popen(cmd_args)
    
    return kwargs["BUILDBOT_PORT"]

def buildbot_stop_API(**kwargs):
    url = "http://localhost:{BUILDBOT_PORT}/shutdown"
    r = requests.post(url.format(**kwargs))
    msg = "Stoping buildbot instance on port {BUILDBOT_PORT}"
    logging.info(msg.format(**kwargs))
    return r.text
    
####################################################################


def buildbot_ps():
    '''
    Uses UNIX ps to determine which python Flask were launched,
    and what ports they were mapped to.
    '''
    
    cmd_args = ['ps', '-Af']
    shell  = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
    output = shell.communicate()[0].strip().split('\n')

    search_string = "gunicorn " + _WSGI_HEADER
    data = set()

    for item in output[1:]:  # First row is a header
        if search_string not in item:
            continue
        if "python" not in item:
            continue

        item = item.split()
        bind_string = item[item.index("--bind")+1]
        port = bind_string.split(':')[-1]
        data.add(port)
        #package_name = item[item.index("--buildbot_package")+1]
        #data[port] = "package" #package_name

    return data

def list_buildbot_ports():
    '''
    Lists all ports used by buildbot Flask apps.
    '''
    return sorted(list(buildbot_ps()))

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

def check_for_required_containers():
    '''
    Checks for any docker containers listed in required_containers
    and pulls them if they are missing.
    '''
    for container_name in _required_containers:
        try:
            docker_inspect(container_name)
            msg = "Found required container {}.".format(container_name)
            logging.debug(msg)
        except subprocess.CalledProcessError:
            msg = "Failed to load container {}.".format(container_name)
            logging.error(msg)
            msg = "Pulling image in 10 seconds if not canceled."
            logging.warning(msg)
            time.sleep(10)
            docker_pull(container_name)
    
#########################################################################
# Run the actions from the command line arguments.
#########################################################################

if args["list"]:
    data = {
        "neo4j"    : docker_reduced_ps(),
        "buildbot" : buildbot_ps()
    }
    print json.dumps(data,indent=2)
    exit(0)

if args["shutdown"]:

    logging.warning("SHUTTING DOWN ALL NEO4J/BB instances")

    data = {
        "neo4j_ports"    : list_neo4j_ports()[::-1],
        "buildbot_ports" : list_buildbot_ports(),
    }

    for port in data["neo4j_ports"]:
        docker_stop_neo4j(NEO4J_PORT=port,**args)
    for port in data["buildbot_ports"]:
        buildbot_stop_API(BUILDBOT_PORT=port)
    print json.dumps(data,indent=2)
    exit(0)

# Check and pull any missing containers
check_for_required_containers()

####################################################################
        
if args["start"] is not None:
    n_args = len(args["start"])
    f_package,neo4j_db = args["start"]

    '''
    cmd_args = 'gunicorn wsgi:app --bind 0.0.0.0:{}'
    cmd_args = cmd_args.format(next_open_buildbot_port())
    
    subprocess.Popen(cmd_args,shell=True)
    print 
    print cmd_args
    exit()
    #subprocess.Popen(' '.join(cmd_args),shell=True)
    os.system(cmd_args)
    print {"ugly":"bash"}
    exit(0)
    ### DEBUG ABOVE
    '''

    data = {
        "NEO4J_PORT" : next_open_neo4j_port(),
        "NEO4J_DATABASE_LOCATION" : neo4j_db,
        "NEO4J_ADDR" : "localhost",
        "BUILDBOT_PORT" : next_open_buildbot_port(), 
        "BUILDBOT_PACKAGE" : f_package,
    }

    #ID = docker_start_neo4j(**data)
    #msg = "Started docker:neo4j {}".format(ID.strip())
    #logging.info(msg)

    #wait_until_neo4j_is_up(**data)
    #logging.info("neo4j connection established!")

    ID = buildbot_start_API(**data)
    msg = "Started buildbot:{}".format(ID.strip())
    logging.info(msg)
    exit()
    
    print json.dumps(data, indent=2)
    exit(0)
    
'''

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

'''
