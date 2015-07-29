Install notes for docker on Ubuntu 14.04
  
    sudo apt-get install docker
    [restart]
    docker build .
    sudo gpasswd -a [username] docker
    [restart]

Lightwight JDK build: Dockerfile
  
    FROM gliderlabs/alpine
    RUN  apk-install openjdk7-jre-base
    ENTRYPOINT [ "java" ]

Instal with

    docker build -t minimal_openjdk7 -f Dockerfile_JDK .

> Shell script to kill everything Docker related (Nuke from orbit)
  
    #!/bin/bash
    # Stop all running containers
    docker stop $(docker ps -a -q)
    # Delete all containers
    docker rm $(docker ps -a -q) -f
    # Delete all images
    docker rmi $(docker images -q) -f
