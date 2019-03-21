#! /usr/bin/bash

image_tag="clang_image:latest"
container_name="clang"
export DISPLAY=10.128.26.56:0.0

echo " ======== Starting Docker container with name: $container_name =============="

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -e DISPLAY=$DISPLAY -d --name $container_name \
-v c:\\pDisk\\atPipeline\\docker\\clang_container\\third-party-libs:/libs \
-v c:\\pDisk\\atPipeline\\docker\\clang_container\\build:/build \
-v c:\\data:/data \
-it $image_tag 

#docker exec -t clang /build/build.bash

echo "========= Done ========"
