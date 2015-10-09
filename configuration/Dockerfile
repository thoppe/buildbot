# DOCKER-VERSION 0.11.1
# This base images use a "correct" version of ubuntu 
FROM phusion/passenger-full:0.9.16

# I tested the images with theser commands
# docker build -t buildbot_API .
# docker run --link buildbot_neo4j:NEO4J --rm -t -i buildbot_API bash -l
MAINTAINER Travis Hoppe

# Setup a python development env
RUN apt-get -qq update && \
    apt-get install -y \
    	    python-setuptools fabric
RUN easy_install pip
RUN pip install --upgrade pip

# Build the python requirements
WORKDIR /docker/app/
COPY requirements.txt /docker/app/
RUN pip install -r requirements.txt 

# Copy the local files into our running directory
COPY fabfile.py /docker/app/
COPY README.md /docker/app/
COPY configuration_notes.md /docker/app/
COPY buildbot /docker/app/buildbot/

EXPOSE 5000
EXPOSE 80

CMD ["fab", "api"]