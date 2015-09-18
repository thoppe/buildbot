# BuildBot
_(the backend of FABRIC)_

----------
#### [Travis Hoppe](http://thoppe.github.io/)
#### [Mitchell Harris](xxx)

====

### Let's build an app!

|Ingredients:
|##### An idea
|##### A knowledge of the full stack
|front-end, back-end, server hosting, OS, security, UX, UI, ...

Not everyone with an idea is a full-stack developer!
Empathetic software...
  
====

## *BuildBot*
# Turning<br>configuration<br>into design.

====*

## A design problem?

#### What is the data?
!(images/graph_schema.png)
#### How is the data related?

%  Natural representation as a graphDB.

====*

## Describe the data

What is a `job`? What is a `person`?

    "job" : {
        "description" : "",
        "title"  : "Unassigned"
    },
  
    "person" : {
        "@context": "http://schema.org",
        "@type": "Person",
        "name" : "",
        "username" : "",
        "userid" : 0
    },

Natural language description infers types and defaults.
Capability to handle JSON-LD like those from [schema.org](http://schema.org).

====*

## What does BuildBot _do_?

From a package:

+ Creates a isolated dockerized neo4j database.
+ Establishes a RESTful API for standard operations (create, delete, update).
+ Connects any external API and enforces contracts via swagger files.
+ Creates API endpoints from high-level descriptions of logic.

Want more?

+ Template the logic (node.js, python)? BuildBot will execute it when called via the API.
+ API calls can be chained together, completely mimicking others like Elastic.io and IFTT.
+ Detailed RFPs can be auto generated!
+ Site mock-ups can be inferred and will function live!

+ A package is stored internally in git -- automatic source control!
+ Packages can be built from each other, automatic imports!

====*
# Contracts

Enforcement of contraints from one API to another. 

    "contracts" : [
        "contracts/ipify.swagger" 
    ],
  
====*
# Logic
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

====*

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

# Thank you.