# BuildBot
_(the backend of FABRIC)_

----------
#### [Travis Hoppe](http://thoppe.github.io/) 
#### [Mitchell Harris](https://angel.co/mitharris)

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

## *BuildBot Design*
  
## Data + Contracts + Logic
%## (you) + (us) + (them) 

====

## Step #1: Data

#### Describe the data.
#### Describe how the the data related?
!(images/graph_schema.png)
% Example project management app.
%  Natural representation as a graphDB.

====*

## Describe the data

Natural language description infers types and defaults.
Capability to handle JSON-LD like those from [schema.org](http://schema.org).

What is a `job`?
    "job" : {
        "description" : "",
        "title"  : "Unassigned"
    },

What is a `person`?  
    "person" : {
        "@context": "http://schema.org",
        "@type": "Person",
        "name" : "",
        "username" : "",
        "userid" : 0
    },

====

## Step #2: Contracts 

Leverage emerging industry standard, [swagger](http://swagger.io/).

Enforcement of contraints from one API to another.    
  
They can be quite complicated! 
      "paths": {
        "/": {
            "get": {
                "description": "Using ipify is ridiculously simple. You have three options. You can get your public IP directly (in plain text), you can get your public IP in JSON format, or you can get your public IP information in JSONP format (useful for Javascript developers).",
                "produces": [
                    "application/json",
                    "text/xml"
                ],
                "parameters": [
                    {
                        "name": "format",
                        "in": "query",
                ...
====

### Contracts in BuildBot

Local or publicaly accessible URLS:  

    "contracts" : [
        "contracts/ipify.swagger" 
    ],
   
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

## What does BuildBot _do_?

### Persistant, presonalizted data storage
+ Creates a isolated dockerized neo4j database.

  
### Standard data interactions.
+ Establishes a RESTful API for standard operations (create, delete, update).

  
### Efficicent pass through of extenral data
+ Connects any external API and enforces contracts via swagger files.

  
### Templating functionality
+ Creates API endpoints from high-level descriptions of logic.

  
====*

## What _will_ BuildBot do?

+ Fill in the logic (node.js, python)? BuildBot will execute it when called via the API.
  
+ Chain API calls together, mimicking others like Elastic.io and IFTT.
  
+ Generate detailed RFPs automatically.
  
+ Site mock-ups can be inferred and will function live!

+ A package is stored internally in git -- automatic source control!

+ Packages can be built from each other, automatic imports!

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