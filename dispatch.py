import argparse, subprocess

desc = '''Dispatcher for BuildBot'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--list',
                    default=False,
                    action='store_true',
                    help='Returns the running buildbot instances.')
args = vars(parser.parse_args())

def docker_ps():
    '''
    Returns the output 
    '''

if args["list"]:
    names = ["ID", "Image", "Command", "CreatedAt", "RunningFor",
             "Ports", "Status", "Size", "Labels"]
    format_string = ','.join(["{{.%s}}"%x for x in names])
    cmd = 'docker ps -a --format ' + format_string
    output = subprocess.check_output(cmd, shell=True)
    data   = [dict(zip(names, line))
              for line in output.strip().split('\n')]
    #header,data = lines[0], lines[1:]
    print data
    




