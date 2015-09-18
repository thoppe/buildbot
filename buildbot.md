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
A protocal describing an API interface.

Pros: 
Machine interface for API calls, automatic documentation, code templating!
  
Cons: They can be quite complicated! 
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

====

### Contracts in BuildBot
BuildBot automaticlly generates swagger files from a simple package file.

Link to local swagger files or publicaly accessible URLS:  
    "contracts" : [
        "contracts/ipify.swagger" 
    ],

All API calls are type-checked through the swagger file ensuring data consistancy. 

   
====*
  
## Step #3: Logic
  
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
        "IP_address" : data.ip,
        "timestamp"  : d.getTime(),
        "name" : data.name,
      }
      return output;   
    };

====

### Example documentation 
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

Exported swagger file from package:
[https://raw.githubusercontent.com/tulsa/demo_swagger_files/master/swagger.json](https://raw.githubusercontent.com/tulsa/demo_swagger_files/master/swagger.json)

[Automatic documentation](http://petstore.swagger.io/)

====

## What does BuildBot _do_?

### Persistant, presonalizted data storage
+ Creates a isolated dockerized neo4j database.

  
### Standard data interactions.
+ Establishes a RESTful API for standard operations (create, delete, update).

  
### Efficicent pass through of extenral data
+ Connects any external API and enforces contracts via swagger files.

  
### Templating functionality
+ Creates API endpoints from high-level descriptions of logic
  
====*

## What _will_ BuildBot do?

### Complex multi-domain actions 
+ Chain API calls together, mimicking others like [Elastic.io](http://www.elastic.io/) and [IFTT](https://ifttt.com/).


### Project planning
+ Generate detailed [RFPs](https://en.wikipedia.org/wiki/Request_for_proposal) automatically.

  
### Project templating
+ Infer a site mock-up that functions live.


### Leverage exisiting apps
Packages stored internally in git, automatic source control and
importing from other packages can expand functionality.

====

Where to go from here?
  
18f?

    
====

But, but, but! Questions!

My data is not a graph!
(doesn't matter)

Will this scale?
(no, but it doesn't matter)
  
Hasn't this been done before?
(maybe, ...)

====

# Thanks, you.