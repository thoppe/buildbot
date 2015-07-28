#Docker install instructions

docker pull tpires/neo4j

# Note that the port is changed so it doesn't conflict with the local install
docker run -i -t -d --name neo4j_1 --cap-add=SYS_RESOURCE -p 7475:7474 tpires/neo4j

# http://localhost:7475/browser/

# Run this with our username and password
docker run -i -t -d -e NEO4J_AUTH=neo4j:tulsa --name neo4j --cap-add=SYS_RESOURCE -p 7474:7474 tpires/neo4j