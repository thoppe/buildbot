FROM ubuntu:14.04

# Set the enviorment to something nicer
ENV TERM linux
  
# OS config
# RUN apt-get update && apt-get upgrade -y && apt-get install wget -y
RUN apt-get install wget -y

# Install Neo4j
RUN wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add - && \
    echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list && \
    apt-get update ; apt-get install neo4j -y


# Expose the Neo4j browser to the host OS on port 7474
EXPOSE 7474