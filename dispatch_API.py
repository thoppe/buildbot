#!flask/bin/python
import subprocess, logging, json, os
import flask
from flask import Flask, request, abort, render_template, redirect, jsonify, url_for

from celery import Celery


_dispatch_version = 1.0
_dispatch_port = 2001

# Flask entry point
API = Flask(__name__)
API.logger.setLevel(logging.INFO)

API.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
API.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(API.name, broker=API.config['CELERY_BROKER_URL'])
celery.conf.update(API.config)

homepage = '''
<h1>buildbot dispatch API version {}</h1>

<ul>
  <li><a href="/list"><code>/list</code></a></li>
  <li><a href="/shutdown"><code>/shutdown</code></a></li>
  <li><a href="/create_test_instance"><code>/create_test_instance</code></a></li>
</ul>
'''.format(_dispatch_version)


import time

'''
@celery.task(bind=True)
def sample_task(self, x):
    
    self.update_state(
        state="starting...",
        meta={"token":0}
    )

    for i in range(x):
        print i,x
        time.sleep(1)

        self.update_state(
            state="working...",
            meta={"token":i}
        )

    results = [i,]
    return results
'''

@API.route('/status/<task_id>')
def taskstatus_dispatch(task_id):
    
    task = run_dispatch_async.AsyncResult(task_id)
    
    response = {
        "state" : task.state,
        "id" : task.id,
        "backend" : str(task.backend),
        "meta": task.info,
    }

    #if response["state"] == "SUCCESS":
    #    response["result"] = task.result
    
    return jsonify(response)


###################################################################

def run_dispatch(sub_args):
    output = subprocess.check_output(sub_args)
    js = json.loads(output)
    return jsonify(**js)

@celery.task(bind=True)
def run_dispatch_async(self,*args):
    sub_args = ['./dispatch.py'] + list(args)

    self.update_state(
        state="RUNNING",
        meta={"cmd":sub_args}
    )
    
    output = subprocess.check_output(sub_args)
    js = json.loads(output)

    self.update_state(
        state="FINISHED",
        meta={"cmd":sub_args}
    )
    
    return jsonify(**js)

###################################################################

@API.route('/')
def root_page():
    return homepage

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

    # Start the task async
    args = ("--start",bb_package,db_loc)
    task = run_dispatch_async.apply_async(args)

    url = url_for('taskstatus_dispatch',task_id=task.id)
    
    # For test purposes return a clickable link!
    html =  '''<a href={}>celery status</a>'''
    return html.format(url)
    
    # JSONify the return params
    js = {
        "url" : url, 
    }

    return jsonify(**js)

if __name__ == "__main__":

    API.run(
        port  = _dispatch_port,
        debug = True,
    )
