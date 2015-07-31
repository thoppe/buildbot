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

#!flask/bin/python
from flask import Flask, request, abort
API = Flask(__name__)

#tapp = app.test_client()

@API.route('/buildbot/api/v1.0/relationship/create', methods=['POST'])
def create_relationship():
    js = request.get_json()

    for key in ["label", "start_id", "end_id"]:
        if key not in js: abort(400)

    # Query the nodes
    node1 = interface.convert_neo4j2node(gdb[js["start_id"]])
    node2 = interface.convert_neo4j2node(gdb[js["end_id"]])

    # Build a relationship object
    js["start"] = node1.label
    js["end"]   = node2.label
    rel = interface.convert_json2edge_container(json.dumps(js),True)

    rel = gdb.add_relationship(rel)
    js_out = interface.convert_edge_container2json(rel)

    return js_out, 201

@API.route('/buildbot/api/v1.0/relationship/remove/<int:rel_id>',
           methods=['POST'])
def remove_relationship(rel_id):
    result = gdb.remove_relationship(rel_id)
    return json.dumps(result), 200

###########################################################################

@API.route('/buildbot/api/v1.0/node/<int:node_id>', methods=['GET'])
def get_node(node_id):
    obj  = gdb[node_id]    
    node = interface.convert_neo4j2node(obj)
    js   = interface.convert_node_container2json(node)
    return js, 200

@API.route('/buildbot/api/v1.0/node/remove/<int:node_id>', methods=['POST'])
def remove_node(node_id):
    result = gdb.remove_node(node_id)
    return json.dumps(result), 200

@API.route('/buildbot/api/v1.0/node/create', methods=['POST'])
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

@API.route('/buildbot/api/v1.0/node/update', methods=['POST'])
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

    js = interface.convert_node_container2json(node)
    return js, 201

###########################################################################

'''
def test_update_node(test_data):
    print "Update node"
    json_string = json.dumps(test_data)
    response = tapp.post('/buildbot/api/v1.0/node/update',
                        data=json_string,
                        content_type='application/json')
    return response.data

def test_remove_relationship(rel_id):
    print "Remove relationship", rel_id
    url = '/buildbot/api/v1.0/relationship/remove/{}'.format(rel_id)
    response = tapp.post(url)
    return response.data


test_flow_data1 = {"description": "unittest", "label": "flow",
             "status": 0.75, "validation": "unittest", "version": 0.2}
    
test_flow_data2 = {"description": "unittest", "label": "flow",
                    "status": 0.99, "validation": "unittest", "version": 0.3}

##############################################################################

# Change the status
test_flow_data1["status"] = .20
test_flow_data1["id"] = node1.id
print test_update_node(test_flow_data1)

# Add a second flow node
js_node2 = test_create_node(test_flow_data2)
node2 = interface.convert_json2node_container(js_node2)

test_flow_link_data = {"label":"depends",
                       "start_id":node1.id,
                       "end_id"  :node2.id}

js_rel1 = test_create_relationship(test_flow_link_data)
rel = interface.convert_json2edge_container(js_rel1)

test_remove_relationship(rel.id)
exit()


# Remove the nodes (this fails now when there is a relationship joining them!
print test_remove_node(node1.id)
print test_remove_node(node2.id)
'''

'''
#import logging, sys
#app.logger.addHandler(logging.StreamHandler(sys.stdout))
#app.logger.setLevel(logging.DEBUG)
#if __name__ == '__main__':
#    app.run(debug=True, use_reloader=False)
'''
