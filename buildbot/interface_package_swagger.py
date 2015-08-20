from REST_API_buildbot import API_DOCS, gdb, neo4j_login


S = {}
S["swagger"]  = 2.0
S["basePath"] = "/"
S["info"] = {
    "title" : gdb.package.meta["package_name"],
    "description" : gdb.package.meta["package_author"],
}

S["host"] = "http://0.0.0.0:5000/"
S["produces"] = ["application/json",]
S["paths"] = {}



print neo4j_login
print S
