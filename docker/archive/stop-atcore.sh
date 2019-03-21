#!/usr/bin/env bash

container_name="atcore"
running_status=`docker inspect -f '{{.State.Running}}' $container_name`
if [ $running_status == "true" ];
then
    echo "==== Stopping docker container: $container_name ===="
    docker stop $container_name
else
    echo "Container: $container_name is not running"
fi    


