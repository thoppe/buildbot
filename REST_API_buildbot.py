import os, json

from buildbot.utils import neo4j_credentials_from_env
from buildbot.graphDB import enhanced_GraphDatabase
from buildbot.data_schema import defined_nodes
import buildbot.interface_neo4j_json as interface

DOCKER_ENV = {
    "NEO4J_DATABASE_DIR" : os.path.join(os.getcwd(), "database/"),
    "NEO4J_PORT"     : 7475,
    "NEO4J_USERNAME" : "buildbot",
    "NEO4J_PASSWORD" : "tulsa",
}

# Export the DOCKER enviorment variables
for key,val in DOCKER_ENV.items():
    os.environ[key] = str(val)

neo4j_login = neo4j_credentials_from_env()
gdb = enhanced_GraphDatabase(**neo4j_login)

## TEST CODE HERE

#!flask/bin/python
from flask import Flask, request, abort
app = Flask(__name__)
tapp = app.test_client()

# Test with
#curl -i http://localhost:5000/buildbot/api/v1.0/node/30

@app.route('/buildbot/api/v1.0/node/<int:node_id>', methods=['GET'])
def get_node(node_id):
    obj = gdb[node_id]
    node = interface.convert_neo4j2node(obj)
    js = interface.convert_node_container2json(node)
    return js, 200

@app.route('/buildbot/api/v1.0/node', methods=['POST'])
def create_node():
    js = request.get_json()
    
    if 'label' not in js:
       abort(400)

    json_text = json.dumps(js)
    node = interface.convert_json2node_container(json_text,
                                                 ignore_id_check=True)
    
    # Add the node and set the ID
    node = gdb.add_node(node)
    js = interface.convert_node_container2json(node)
    return js, 201


def test_get_node(node_id):
    print "Get Node"
    url = '/buildbot/api/v1.0/node/{}'.format(node_id)
    response = tapp.get(url)
    return response.data

def test_create_node(test_data):
    print "Creating node"
    json_string = json.dumps(test_data)
    response = tapp.post('/buildbot/api/v1.0/node',
                        data=json_string,
                        content_type='application/json')
    return response.data


 #test_create_node = '''curl -i -H "Content-Type: application/json" -X POST -d '{"description": "unittest", "label": "flow", "status": 0.75, "validation": "unittest", "version": 0.2}' http://localhost:5000/buildbot/api/v1.0/node'''
#test_request_node = "curl -i http://localhost:5000/buildbot/api/v1.0/node/30"

# Create a flow node, get the idx created.
#flow = defined_nodes["flow"]
#node = flow(description="Test flow!",status=0.2)
#obj  = gdb.add_node(node)
#node_id  = obj.id
#print node_id

test_data = {"description": "unittest", "label": "flow", "status": 0.75, "validation": "unittest", "version": 0.2}

js_node = test_create_node(test_data)
node = interface.convert_json2node_container(js_node)
js_node2 = test_get_node(node.id)

assert( js_node == js_node2 )






#import logging, sys
#app.logger.addHandler(logging.StreamHandler(sys.stdout))
#app.logger.setLevel(logging.DEBUG)
#if __name__ == '__main__':
#    app.run(debug=True, use_reloader=False)

