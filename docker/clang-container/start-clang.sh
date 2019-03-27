#! /usr/bin/bash

image="atpipeline/clang:latest"
container_name="clang"
export DISPLAY=$HOSTNAME:0.0

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -e DISPLAY=$DISPLAY -d --name $container_name \
-v /nas:/nas \
-v /nas2:/nas2 \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /nas5:/nas5 \
-v /nas6:/nas6 \
-v /local1:/local1 \
-v /local2:/local2 \
-it $image 

#-v c:\\pDisk\\atPipeline\\docker\\clang-container\\third-party-libs:/libs \
#-v c:\\pDisk\\atPipeline\\docker\\clang-container\\build:/build \

#cp ./build-thirdparty-libs.bash ./build
#docker exec -t clang /build/build-thirdparty-libs.bash
#-v c:\\pDisk\\atPipeline\\docker\\clang_container\\third-party-libs:/libs \
#-v c:\\pDisk\\atPipeline\\docker\\clang_container\\build:/build \

echo "========= Done ========"
