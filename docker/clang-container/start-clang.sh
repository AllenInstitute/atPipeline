#! /usr/bin/bash

image="atpipeline/clang:latest"
container_name="clang"
export DISPLAY=$HOSTNAME:0.0

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -e DISPLAY=$DISPLAY -d --name $container_name \
-v c:\\data:/data \
-it $image 

#-v c:\\pDisk\\atPipeline\\docker\\clang-container\\third-party-libs:/libs \
#-v c:\\pDisk\\atPipeline\\docker\\clang-container\\build:/build \

#cp ./build-thirdparty-libs.bash ./build
#docker exec -t clang /build/build-thirdparty-libs.bash
#-v c:\\pDisk\\atPipeline\\docker\\clang_container\\third-party-libs:/libs \
#-v c:\\pDisk\\atPipeline\\docker\\clang_container\\build:/build \

echo "========= Done ========"