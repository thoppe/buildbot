import json

from buildbot.utils import neo4j_credentials_from_env
from buildbot.graphDB import enhanced_GraphDatabase
import buildbot.interface_neo4j_json as interface

# Startup the database connection
neo4j_login = neo4j_credentials_from_env()
gdb = enhanced_GraphDatabase(**neo4j_login)

#!flask/bin/python
from flask import Flask, request, abort
API = Flask(__name__)

@API.route('/buildbot/api/v1.0/relationship/create', methods=['POST'])
def create_relationship():
    data = request.get_json()

    for key in ["label", "start_id", "end_id"]:
        if key not in data: abort(400)

    # Query the nodes
    node1 = interface.convert_neo4j2node(gdb[data["start_id"]])
    node2 = interface.convert_neo4j2node(gdb[data["end_id"]])

    # Build a relationship object
    data["start"] = node1.label
    data["end"]   = node2.label
    rel = interface.convert_json2edge_container(json.dumps(data),True)

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
    obj     = gdb[node_id]    
    node    = interface.convert_neo4j2node(obj)
    js_out  = interface.convert_node_container2json(node)
    return js_out, 200

@API.route('/buildbot/api/v1.0/node/remove/<int:node_id>', methods=['POST'])
def remove_node(node_id):
    result = gdb.remove_node(node_id)
    return json.dumps(result), 200

@API.route('/buildbot/api/v1.0/node/create', methods=['POST'])
def create_node():
    data = request.get_json()
    
    if 'label' not in data:
       abort(400)

    json_text = json.dumps(data)
    node = interface.convert_json2node_container(json_text,
                                                 ignore_id_check=True)
    
    # Add the node and set the ID
    node = gdb.add_node(node)
    js_out = interface.convert_node_container2json(node)
    return js_out, 201

@API.route('/buildbot/api/v1.0/node/update', methods=['POST'])
def update_node():
    data = request.get_json()
    
    if 'label' not in data and 'id' not in data:
       abort(400)
    
    json_text = json.dumps(data)
    node = interface.convert_json2node_container(json_text)
    
    try:
        node = gdb.update_node(node)
    except Exception as Ex:
        print "Update node {} failed with:".format(node.id), Ex
        abort(404)

    js_out = interface.convert_node_container2json(node)
    return js_out, 201

###########################################################################

if __name__ == "__main__":
    import logging, sys
    #app.logger.addHandler(logging.StreamHandler(sys.stdout))
    #app.logger.setLevel(logging.DEBUG)
    if __name__ == '__main__':
        app.run()
