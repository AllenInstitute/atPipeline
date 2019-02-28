#! /usr/bin/bash

image="atpipeline/atcore"
container_name="atcore"
tag="dev"

echo " ======== Starting Docker container with name: $container_name =============="

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -d --name $container_name \
-v /Users/eric/nobackup:/mnt \
-v /Users/eric/tra/atPipeline/pipeline:/pipeline \
-v /Users/eric/tra/atPipeline/docker/render-python-apps:/usr/local/render-python-apps  \
-i -t $image:$tag /bin/bash

echo "Done.."
