#!flask/bin/python
import subprocess, logging, json, os
from flask import Flask, request, abort, render_template
from flask import redirect, jsonify, url_for
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

def run_dispatch(args):
    sub_args = ['./dispatch.py'] + list(args)
    output = subprocess.check_output(sub_args)
    return json.loads(output)

@celery.task(bind=True)
def run_dispatch_async(self,*args):   
    self.update_state(
        state="RUNNING",
        meta={"dispatch_args":args}
    )

    return run_dispatch(args)

###################################################################

@API.route('/')
def root_page():
    return homepage

@API.route('/list')
def list_pages():
    data = run_dispatch(["-l"])
    return jsonify(data)

@API.route('/shutdown')
def shutdown_all():
    data = run_dispatch(["--shutdown"])
    return jsonify(data)

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
