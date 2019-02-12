#! /usr/bin/bash

#if [[ $(uname -s) == CYGWIN* ]];then
    docker-compose -f ./init/docker-compose-wsl.yml up -d
#else 
#    docker-compose -f ./init/docker-compose-mac.yml up -d
#fi
