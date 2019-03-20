#! /usr/bin/bash

image_tag="clang_image:0.5"
container_name="clang"
export DISPLAY=10.128.26.56:0.0

echo " ======== Starting Docker container with name: $container_name =============="

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -e DISPLAY=$DISPLAY -d --name $container_name \
-v c:\\pDisk\\ATPipeline\\docker\\third-party-libs:/libs \
-v c:\\pDisk\\ATPipeline\\docker\\third-party-libs\\builds:/builds \
-v c:\\data:/data_mount_1 \
-it $image_tag /bin/bash

echo "Done.."
