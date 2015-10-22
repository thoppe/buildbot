#!flask/bin/python
import flask
from flask import Flask, request, abort, render_template, redirect
import logging, json

import subprocess

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
</ul>  

'''.format(_dispatch_version)

@API.route('/')
def root_page():
    return homepage

@API.route('/list')
def list_pages():
    output = subprocess.check_output(['./dispatch.py', '-l'])
    js = json.loads(output)
    return flask.jsonify(**js)

if __name__ == "__main__":

    API.run(
        port  = _dispatch_port,
        debug = True,
    )
