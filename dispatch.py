import argparse, subprocess, json, logging, time
from pprint import pprint

desc = '''Dispatcher for BuildBot'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--list',
                    default=False,
                    action='store_true',
                    help='Returns the running buildbot instances.')
args = vars(parser.parse_args())
logging.basicConfig(level=logging.INFO)

required_containers = [
    'tpires/neo4j',
]

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




