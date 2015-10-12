#!flask/bin/python
from flask import Flask, request, abort, render_template, redirect

import json, logging, argparse, os
from utils import neo4j_credentials_from_env
import graphDB 

'''
The Flask APP needs to be started with the proper enviorment variables set,
or run with command-line arguments.
'''

if __name__ == "__main__":

    desc = '''BuildBot API'''
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--BUILDBOT_PORT','-b',
                        default=None,
                        help="buildbot's port")

    parser.add_argument('--NEO4J_TCP_PORT','-p',
                        default=None,
                        help='NEO4J port')

    parser.add_argument('--NEO4J_TCP_ADDR','-a',
                        default=None,
                        help='NEO4J TCP address')

    parser.add_argument('--NEO4J_AUTH','-l',
                        default=None,
                        help='NEO4J username:password')

    parser.add_argument('--buildbot_package','-f',
                        default=None,
                        help='BuildBot package file to load')

    parser.add_argument('--debug','-d',
                        default=True,
                        action="store_false",
                        help='Turns off debug mode for Flask')

    args = vars(parser.parse_args())
else:
    args = {"debug": True}

'''
Remove command line arguments that are None (they will try to load
from an env variable instead).
'''
none_args = [key for key,val in args.items() if val is None]
for key in none_args:
    del args[key]

#####################################################################

# Fire up a database connection
neo4j_login = neo4j_credentials_from_env(**args)
gdb = graphDB.enhanced_GraphDatabase(**neo4j_login)

#graphDB.hard_reset(gdb)

# Flask entry point
API = Flask(__name__)
API.logger.setLevel(logging.INFO)

info_msg = "Started BuildBot API port:{BUILDBOT_PORT} package:{buildbot_package} debug:{debug}"
all_args = args.copy()
all_args.update(os.environ)
logging.warning(info_msg.format(**all_args))

# Helper functions
import interface_neo4j_json as inter
neo2node  = lambda x:inter.convert_neo4j2node_container(x,gdb.package)
neo2edge  = lambda x:inter.convert_neo4j2edge_container(x,gdb.package)
json2node = lambda x,**a:inter.convert_json2node_container(x,gdb.package,**a)
json2edge = lambda x,**a:inter.convert_json2edge_container(x,gdb.package,**a)

# API_DOCS
rel_API = "<string:start_label>/<string:rel_label>/<string:end_label>"
API_DOCS = {}

API_DOCS["create_node"] = {
    "methods" : ["POST"],
    "description" : "Create a new node.",
    "url" : '/buildbot/api/v1.0/node/<string:label>/create',
    "labels" : gdb.package.nodes.keys()
    }

API_DOCS["update_node"] = {
    "methods" : ["POST"],
    "description" : "Update a node.",
    "url" : '/buildbot/api/v1.0/node/<string:label>/update',
}

API_DOCS["remove_node"] = {
    "methods" : ["DELETE"],
    "description" : "Remove a node.",
    "url" : '/buildbot/api/v1.0/node/<string:label>/remove'
}

API_DOCS["get_node"] = {
    "methods" : ["GET"],
    "description" : "Retrieves a node by index.",
    "url" : '/buildbot/api/v1.0/node/<string:label>/<int:node_id>'
}

API_DOCS["search_node"] = {
    "methods" : ["GET"],
    "description" : "Search for a node, returns node ID.",
    "url" : '/buildbot/api/v1.0/node/<string:label>/search',
    "labels" : gdb.package.nodes.keys()
    }

API_DOCS["create_relationship"] = {
    "methods" : ["POST"],
    "description" : "Create a new relationship.",
    "url" : '/buildbot/api/v1.0/relationship/{}/create'.format(rel_API),
    "labels" : ["{}-[{}]->{}".format(*x) for x in gdb.package.relationships]
}

API_DOCS["remove_relationship"] = {
    "methods" : ["DELETE"],
    "description" : "Remove a relationship.",
    "url" : '/buildbot/api/v1.0/relationship/{}/remove'.format(rel_API),
}

@API.route('/')
def root_page():
    return "Buildbot v1.0"
    return redirect("/help")

@API.route('/help')
def documentation_page():
    data = {}
    data["package_name"]  = gdb.package.meta["package_name"]
    data["package_author"] = gdb.package.meta["package_author"]

    # Set the order to display here!
    key_order = ["create_node", "create_relationship",
                 "get_node", "search_node",
                 "remove_node","remove_relationship",
                 "update_node"
                 ]
    data["API_DOCS"] = [API_DOCS[key] for key in key_order]
    return render_template("API_documentation.html",**data)

@API.route('/help/<string:label>')
def label_documentation_page(label):
    data = {}
    data["package_name"]  = gdb.package.meta["package_name"]
    data["package_author"] = gdb.package.meta["package_author"]
    data["label"] = label

    if "]->" in label:
        obj_type = gdb.package.relationships
        obj_key = (label.split('-[')[0],
                   label.split('-[')[1].split(']->')[0],
                   label.split(']->')[1])
        data["label_type"] = "relationship"
        
    else:
        obj_type = gdb.package.nodes
        obj_key = label
        data["label_type"] = "node"

    obj = obj_type[obj_key](1,1)
    item = {}
    
    for key in obj:
        item[key] = unicode(type(obj[key]).__name__)
    data["label_desc"] = json.dumps(item,indent=2)
    
    return render_template("API_label_doc.html",**data)

###########################################################################

doc_key = "create_relationship"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def create_relationship(start_label, rel_label, end_label):
    data = request.get_json()

    for key in ["start_id", "end_id"]:
        if key not in data: abort(400)

    # Query the nodes
    node1 = neo2node(gdb[data["start_id"]])
    node2 = neo2node(gdb[data["end_id"]])

    # Sanity checks!
    assert(node1.label == start_label)
    assert(node2.label == end_label)

    # Build a relationship object
    data["start"] = node1.label
    data["end"]   = node2.label
    data["label"] = rel_label
    
    rel = json2edge(json.dumps(data),ignore_id_check=True)

    rel = gdb.add_relationship(rel)
    js_out = rel.json()

    return js_out, 201

doc_key = "remove_relationship"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def remove_relationship(start_label, rel_label, end_label):
    data = request.get_json()
    assert("id" in data)
    
    result = gdb.remove_relationship(data["id"])
    return json.dumps(result), 200

###########################################################################

doc_key = "get_node"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def get_node(label, node_id):
    obj     = gdb[node_id]    
    node    = neo2node(obj)
    js_out  = node.json()
    return js_out, 200

doc_key = "search_node"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def search_node(label):
    data = request.get_json()
    if "label" in data:
        data.pop("label")
    result = {"match_nodes":gdb.select(label, **data)}
    js_out = json.dumps(result)
    return js_out, 200

doc_key = "remove_node"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def remove_node(label):
    data = request.get_json()
    assert("id" in data)
    
    # TO DO: Add check if label matches node id!
    result = gdb.remove_node(data["id"])
    return json.dumps(result), 200

doc_key = "create_node"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def create_node(label):
    data = request.get_json()
    
    # Label is implict now
    if 'label' in data and label != data['label']:
       abort(500, "Label mismatch") 

    # Set the label if not in the data
    data["label"] = label

    json_text = json.dumps(data)

    node = json2node(json_text,ignore_id_check=True)
    
    # Add the node and set the ID
    node = gdb.add_node(node)
    js_out = node.json()
    return js_out, 201


doc_key = "update_node"
@API.route(API_DOCS[doc_key]["url"], methods=API_DOCS[doc_key]["methods"])
def update_node(label):
    data = request.get_json()

    if 'label' in data and label != data['label']:
       abort(500, "Label mismatch") 
        
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

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@API.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

###########################################################################


if __name__ == "__main__":

    API.run(
        port =int(args["BUILDBOT_PORT"]),
        debug=args["debug"],
    )

    '''
    # Old inline-test code here
    
    # DEBUG
    API.logger.setLevel(logging.DEBUG)

    # Startup the database connection
    #neo4j_login = neo4j_credentials_from_env()
    #gdb = enhanced_GraphDatabase(**neo4j_login)
    
    import logging, sys
    API.logger.addHandler(logging.StreamHandler(sys.stdout))
    API.logger.setLevel(logging.DEBUG)
    
    # For this to be dockerized, it needs to be seen from
    # the outside world, otherwise we get
    # (56) Recv failure: Connection reset by peer
    #API.run(host='0.0.0.0',debug=True)
    
    data = {"description": "test flow",
            "label": "flow",
            "status": 0.75,
            "validation": "unittest",
            "version": 0.2}
    
    x = API.test_client()
    url = '/buildbot/api/v1.0/node/{label}/create'

    def post(url,data):
        urlx = url.format(**data)
        js = json.dumps(data)
        return x.post(urlx,data=js,content_type='application/json')

    def get(url,data):
        urlx = url.format(**data)
        js = json.dumps(data)
        return x.get(urlx,data=js,content_type='application/json')
        
    response_n1 = post(url,data)
    idx1 = json.loads(response_n1.data)["id"]

    response_n2 = post(url,data)
    idx2 = json.loads(response_n2.data)["id"]

    url = url = '/buildbot/api/v1.0/node/{label}/search'
    search_result = get(url, {"label":"flow","status":0.75})
    print search_result.data

    url = '/buildbot/api/v1.0/node/{label}/update'
    print post(url, json.loads(response_n1.data))

    data = {"start_id":idx1, "end_id":idx2}
    url  = '/buildbot/api/v1.0/relationship/flow/depends/flow/create'
    response = post(url, data)

    url  = '/buildbot/api/v1.0/relationship/flow/depends/flow/remove'
    print post(url, json.loads(response.data))
    
    url = '/buildbot/api/v1.0/node/{label}/remove'
    print post(url, json.loads(response_n1.data))
    print post(url, json.loads(response_n2.data))
    '''
