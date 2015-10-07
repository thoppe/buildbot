import argparse, subprocess
from pprint import pprint

desc = '''Dispatcher for BuildBot'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--list',
                    default=False,
                    action='store_true',
                    help='Returns the running buildbot instances.')
args = vars(parser.parse_args())

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




