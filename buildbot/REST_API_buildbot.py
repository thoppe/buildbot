import json

from utils import neo4j_credentials_from_env
from graphDB import enhanced_GraphDatabase

# Startup the database connection
neo4j_login = neo4j_credentials_from_env()
gdb = enhanced_GraphDatabase(**neo4j_login)

# Helper functions
import interface_neo4j_json as inter
neo2node  = lambda x:inter.convert_neo4j2node_container(x,gdb.package)
neo2edge  = lambda x:inter.convert_neo4j2edge_container(x,gdb.package)
json2node = lambda x,**a:inter.convert_json2node_container(x,gdb.package,**a)
json2edge = lambda x,**a:inter.convert_json2edge_container(x,gdb.package,**a)

# API_DOCS

API_DOCS = {}
API_DOCS["create_node"] = {
    "methods" : "POST",
    "description" : "Create a new node.",
    "url" : '/buildbot/api/v1.0/node/create',
    "labels" : gdb.package.nodes.keys()
    }

API_DOCS["create_relationship"] = {
    "methods" : "POST",
    "description" : "Create a new relationship.",
    "url" : '/buildbot/api/v1.0/relationship/create',
    "labels" : ["{}-[{}]->{}".format(*x) for x in gdb.package.relationships]
}

API_DOCS["update_node"] = {
    "methods" : "POST",
    "description" : "Update a node.",
    "url" : '/buildbot/api/v1.0/node/update',
}

API_DOCS["remove_node"] = {
    "methods" : "POST",
    "description" : "Remove a node.",
    "url" : '/buildbot/api/v1.0/node/remove/<int:node_id>'
}

API_DOCS["remove_relationship"] = {
    "methods" : "POST",
    "description" : "Remove a relationship.",
    "url" : '/buildbot/api/v1.0/relationship/remove/<int:rel_id>'
}

API_DOCS["get_node"] = {
    "methods" : "GET",
    "description" : "Retrieves a node by index.",
    "url" : '/buildbot/api/v1.0/node/<int:node_id>'
}

#!flask/bin/python
from flask import Flask, request, abort, render_template, redirect
API = Flask(__name__)

@API.route('/')
def root_page():
    return redirect("/help")

@API.route('/help')
def documentation_page():
    data = {}
    data["package_name"]  = gdb.package.meta["package_name"]
    data["package_owner"] = gdb.package.meta["package_owner"]

    # Set the order to display here!
    key_order = ["create_node", "create_relationship",
                 "get_node",
                 "remove_node","remove_relationship",
                 "update_node"
                 ]
    data["API_DOCS"] = [API_DOCS[key] for key in key_order]
    return render_template("API_documentation.html",**data)

@API.route('/help/<string:label>')
def label_documentation_page(label):
    s = ''' HERE BOY {} '''.format(label)
    return s

###########################################################################

doc_key = "create_relationship"
@API.route(API_DOCS[doc_key]["url"], methods=[API_DOCS[doc_key]["methods"]])
def create_relationship():
    data = request.get_json()

    for key in ["label", "start_id", "end_id"]:
        if key not in data: abort(400)

    # Query the nodes
    node1 = neo2node(gdb[data["start_id"]])
    node2 = neo2node(gdb[data["end_id"]])

    # Build a relationship object
    data["start"] = node1.label
    data["end"]   = node2.label
    rel = json2edge(json.dumps(data),ignore_id_check=True)

    rel = gdb.add_relationship(rel)
    js_out = rel.json()

    return js_out, 201

doc_key = "remove_relationship"
@API.route(API_DOCS[doc_key]["url"], methods=[API_DOCS[doc_key]["methods"]])
def remove_relationship(rel_id):
    result = gdb.remove_relationship(rel_id)
    return json.dumps(result), 200

###########################################################################

doc_key = "get_node"
@API.route(API_DOCS[doc_key]["url"], methods=[API_DOCS[doc_key]["methods"]])
def get_node(node_id):
    obj     = gdb[node_id]    
    node    = neo2node(obj)
    js_out  = node.json()
    return js_out, 200

doc_key = "remove_node"
@API.route(API_DOCS[doc_key]["url"], methods=[API_DOCS[doc_key]["methods"]])
def remove_node(node_id):
    result = gdb.remove_node(node_id)
    return json.dumps(result), 200

doc_key = "create_node"
@API.route(API_DOCS[doc_key]["url"], methods=[API_DOCS[doc_key]["methods"]])
def create_node():
    data = request.get_json()
    
    if 'label' not in data:
       abort(400)

    json_text = json.dumps(data)
    node = json2node(json_text,ignore_id_check=True)
    
    # Add the node and set the ID
    node = gdb.add_node(node)
    js_out = node.json()
    return js_out, 201


doc_key = "update_node"
@API.route(API_DOCS[doc_key]["url"], methods=[API_DOCS[doc_key]["methods"]])
def update_node():
    data = request.get_json()
    
    if 'label' not in data and 'id' not in data:
       abort(400)
    
    json_text = json.dumps(data)
    node = json2node(json_text)
    
    try:
        node = gdb.update_node(node)
    except Exception as Ex:
        print "Update node {} failed with:".format(node.id), Ex
        abort(404)

    js_out = node.json()
    return js_out, 201

###########################################################################

if __name__ == "__main__":
    import logging, sys
    API.logger.addHandler(logging.StreamHandler(sys.stdout))
    API.logger.setLevel(logging.DEBUG)
    if __name__ == '__main__':
        # For this to be dockerized, it needs to be seen from
        # the outside world, otherwise we get
        # (56) Recv failure: Connection reset by peer

        API.run(host='0.0.0.0',debug=True)
