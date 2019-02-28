#! /usr/bin/bash

image_tag="atpipeline/atcore:dev"
container_name="atcore"

echo " ======== Starting Docker container with name: $container_name =============="

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -d --name $container_name \
-v c:\\data:/mnt  \
-v c:\\pDisk\\ATPipeline\\pipeline:/pipeline  \
-i -t $image_tag /bin/bash

echo "Done.."
