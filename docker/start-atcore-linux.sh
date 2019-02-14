#!/usr/bin/env bash

#Pull image from DOCKER HUB 
image_tag="atpipeline/atcore"
container_name="atcore"
running_status=`docker inspect -f '{{.State.Running}}' $container_name`
if [ $running_status == "true" ];
then
    echo "==== KILLING docker container: $container_name ===="
    docker kill $container_name
fi    

docker rm $container_name 

echo " ==== STARTING docker container: $container_name ===="
docker run -d --name $container_name \
-v /c/data:/mnt/  \
-v $PWD/../pipeline:/pipeline  \
-v $PWD/render-python-apps:/shared/render-python-apps  \
-v $PWD/render-modules:/shared/render-modules  \
-i -t $image_tag /bin/bash

echo " ==== STARTED docker container: $container_name ===="
