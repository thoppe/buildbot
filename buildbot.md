# BuildBot
_(the backend of FABRIC)_

----------
#### [Travis Hoppe](http://thoppe.github.io/) 
#### [Mitchell Harris](https://angel.co/mitharris)

====

### "I've got an idea for an app..."
!(images/full_stack.jpg) Not everyone with an idea is a full-stack developer!



### Question: How do we turn an idea into a prototype? 

%Empathetic software...
  
====

## *BuildBot*
# Turning<br>configuration<br>into design.

====*

## *BuildBot Design*
  
## Data + Contracts + Logic
%## (you) + (us) + (them) 

====

## Step #1: Data

#### Describe the data.
!(images/graph_schema.png)
#### Describe how the data is related.

% Example project management app.
%  Natural representation as a graphDB.

====*

## Describe the data in detail

What is a `job`?
    "job" : {
        "description" : "",
        "title"  : "Unassigned"
    },
Natural description infers types and defaults.  


What is a `person`?  
    "person" : {
        "@context": "http://schema.org",
        "@type": "Person",
        "name" : "",
        "username" : "",
        "userid" : 0
    },
Capability to handle JSON-LD like those from [schema.org](http://schema.org).

====

## Step #2: Contracts 

Leverage emerging industry standard for API communication, 

!(images/swagger-logo.png)<<height:200px;transparent>> 
## [swagger.io](http://swagger.io/)

====*

### What is swagger?
A protocol describing an API interface.

#### Pros: Auto Docs, interface for API calls, and code templating!
  
#### Cons: Complicated & cumbersome...
    "paths": {
        "/statuses/mentions_timeline": {
            "get": {
                "description": "Returns the 20 most recent mentions for the authenticating user",
                "security": [
                    {
                        "oauth": [
                            "basic"
                        ]
                    }
                ],
                "parameters": [
                    {
                        "name": "count",
                        "in": "query",
                        "description": "Specifies the number of tweets to try and retrieve",
                        "required": false,
                        "type": "string"
                    },

====*

### Contracts in BuildBot
BuildBot automatically generates swagger files from a simple package file.

Link to local swagger files or publicly accessible URLS:  
    "contracts" : [
        "contracts/ipify.swagger" 
    ],

External contracts (swagger files) only need to be written once and can be shared.

All API calls are type-checked through the swagger file ensuring data consistency. 

   
====
  
## Step #3: Logic
Specify the only pre & post conditions, types inferred and checked from contracts.
  
package def: 
    "actions" : { 
        "pingme" : {
            "pre" : "https://api.ipify.org?format=json",
            "post": "/node/ping/create",
            "input"  : ["name"],
            "output" : ["IP_address", "timestamp","name"],
            "description" : "Records an IP address and time."
        }
    }

logic (optional):
    exports.pingme = function (data) {
      var d = new Date();
      output = {
        "IP_address" : data.IP,
        "timestamp"  : d.getTime(),
        "name" : data.name,
      }
      return output;   
    };

====

## What does BuildBot _do_?

### Persistent, personalized data storage
+ Creates a isolated dockerized neo4j database.

  
### Standard data interactions.
+ Establishes a RESTful API for standard (create, delete, update) operations.

  
### Connect external data sources
+ Connects any external API and enforces contracts via swagger files.

  
### Logic templating
+ Creates API endpoints from high-level descriptions of desired actions.
  
====*

## What _will_ BuildBot do?

### Project templating
+ Infer a site mock-up that functions live.


### Project planning
+ Generate detailed [RFPs](https://en.wikipedia.org/wiki/Request_for_proposal) automatically.


### Complex multi-domain actions 
+ Chain API calls together, mimicking [Elastic.io](http://www.elastic.io/) and [IFTT](https://ifttt.com/).

    
### Modular design, leverage prior work
Automatic source control & importing from other packages.

====

### Minimal example
    {
    "meta" : {
        "title"       : "checkin",
        "author"      : "thoppe",
        "description" : "Logs your IP address and a timestamp.",
        "version"     : "0.0.1"
    },
    "requires" : [],
    "code_entry" : "packages/checkin/logic.js",
    
    "nodes" : {
        "ping" : {
            "name"       : "",
            "IP_address" : "",
            "timestamp"  : 0
        }
    },
    "relationships" : [ ],
    "contracts" : [
        "contracts/ipify.swagger" 
    ],
    "actions" : {
        "pingme" : {
            "pre" : "https://api.ipify.org?format=json",
            "post": "/node/ping/create",
            "input"  : ["name"],
            "output" : ["IP_address", "timestamp","name"],
            "description" : "Records an IP address and time."
        }
    }
    }

swagger export: [https://raw.githubusercontent.com/tulsa/demo_swagger_files/master/swagger.json](https://raw.githubusercontent.com/tulsa/demo_swagger_files/master/swagger.json)

### [Automatic documentation](http://petstore.swagger.io/)

====

# *BuildBot* + *Fabric*

BuildBot is the backend, CLI, for the hobbyist.

Fabric is the frontend, UI, graphical packages design.
  
====

# FAQ

My data is not a graph! (doesn't matter)

Will this scale? (no, but it doesn't matter)

Isn't Fabric already taken? (Fab.RC)
  
Hasn't this been done before? (maybe, ...)
  

====

# Thanks, you.