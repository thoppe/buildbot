import os
from fabric.api import *

test_directory = "buildbot_flows/test"
test_order = [
    "test_interface.py",
    "test_graph.py",
]

def test():
    test_str = ' '.join([os.path.join(test_directory,x) for x in test_order])
    local("nosetests-2.7 -x -s -v {}".format(test_str))

def clean():
    local("find . -name '*~' | xargs -I {} rm -vf {}")
    local("find . -name '*.pyc' | xargs -I {} rm -vf {}")

def push():
    local("nosetests-2.7")
    local("git status")
    local("git commit -a")
    local("git push")
