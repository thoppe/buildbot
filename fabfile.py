from fabric.api import *

def test():
    local("nosetests-2.7 -s -v ")

def clean():
    local("find . -name '*~' | xargs -I {} rm -vf {}")
    local("find . -name '*.pyc' | xargs -I {} rm -vf {}")

def push():
    local("nosetests-2.7")
    local("git status")
    local("git commit -a")
    local("git push")
