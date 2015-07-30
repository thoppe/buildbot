import os, json

from buildbot.utils import neo4j_credentials_from_env
from buildbot.graphDB import enhanced_GraphDatabase, hard_reset
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

#hard_reset(gdb)
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

@app.route('/buildbot/api/v1.0/node/delete/<int:node_id>', methods=['POST'])
def delete_node(node_id):
    result = gdb.remove_node(node_id)
    return json.dumps(result), 200

@app.route('/buildbot/api/v1.0/node/create', methods=['POST'])
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

@app.route('/buildbot/api/v1.0/node/update', methods=['POST'])
def update_node():
    js = request.get_json()
    
    if 'label' not in js and 'id' not in js:
       abort(400)
    
    json_text = json.dumps(js)
    node = interface.convert_json2node_container(json_text)
    
    try:
        node = gdb.update_node(node)
    except Exception as Ex:
        print "Update node {} failed with:".format(node.id), Ex
        abort(404)

    node = gdb.add_node(node)
    js = interface.convert_node_container2json(node)
    return js, 201

###########################################################################

def test_get_node(node_id):
    print "Get Node", node_id
    url = '/buildbot/api/v1.0/node/{}'.format(node_id)
    response = tapp.get(url)
    return response.data

def test_delete_node(node_id):
    print "Delete Node"
    url = '/buildbot/api/v1.0/node/delete/{}'.format(node_id)
    response = tapp.post(url)
    return response.data

def test_create_node(test_data):
    print "Creating node"
    json_string = json.dumps(test_data)
    response = tapp.post('/buildbot/api/v1.0/node/create',
                        data=json_string,
                        content_type='application/json')
    return response.data

def test_update_node(test_data):
    print "Update node"
    json_string = json.dumps(test_data)
    response = tapp.post('/buildbot/api/v1.0/node/update',
                        data=json_string,
                        content_type='application/json')
    return response.data


test_data = {"description": "unittest", "label": "flow",
             "status": 0.75, "validation": "unittest", "version": 0.2}

js_node = test_create_node(test_data)
print js_node

node = interface.convert_json2node_container(js_node)
js_node2 = test_get_node(node.id)
print js_node2

# Check that they match
assert( js_node == js_node2 )

# Change the status
test_data["status"] = .20
test_data["id"] = node.id
print test_update_node(test_data)

# Delete the node
print test_delete_node(node.id)


'''
#import logging, sys
#app.logger.addHandler(logging.StreamHandler(sys.stdout))
#app.logger.setLevel(logging.DEBUG)
#if __name__ == '__main__':
#    app.run(debug=True, use_reloader=False)
'''
