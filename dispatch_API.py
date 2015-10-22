#!flask/bin/python
import subprocess, logging, json, os
import flask
from flask import Flask, request, abort, render_template, redirect, jsonify


_dispatch_version = 1.0
_dispatch_port = 2001

# Flask entry point
API = Flask(__name__)
API.logger.setLevel(logging.INFO)

homepage = '''
<h1>buildbot dispatch API version {}</h1>

<ul>
  <li><a href="/list"><code>/list</code></a></li>
  <li><a href="/shutdown"><code>/shutdown</code></a></li>
  <li><a href="/create_test_instance"><code>/create_test_instance</code></a></li>
</ul>  

'''.format(_dispatch_version)

@API.route('/')
def root_page():
    return homepage

def run_dispatch(*args):
    sub_args = ['./dispatch.py'] + list(args)
    output = subprocess.check_output(sub_args)
    js = json.loads(output)
    return jsonify(**js)

@API.route('/list')
def list_pages():
    return run_dispatch("-l")

@API.route('/shutdown')
def shutdown_all():
    return run_dispatch("--shutdown")

@API.route('/create_test_instance')
def create_test_instance():
    bb_package = "packages/checkin/checkin.json"
    db_loc = os.path.join(os.getcwd(), "database/db1")
    return run_dispatch("--start",bb_package,db_loc)

if __name__ == "__main__":

    API.run(
        port  = _dispatch_port,
        debug = True,
    )
