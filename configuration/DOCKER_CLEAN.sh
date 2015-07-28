#!/bin/bash
# Stop all running containers
docker stop $(docker ps -a -q)
# Delete all containers
docker rm $(docker ps -a -q) -f
# Delete all images
docker rmi $(docker images -q) -f
