#! /usr/bin/bash
BUILD=${1:-false}
echo "Build flag is "$BUILD

#RENDER PYTHON APPS
image_tag="tottekarlsson/render-python-apps:multi-channel-correction"
container_name="rpa"

echo " ======== Building and starting Docker container with name: $container_name =============="

if [ $BUILD == "true" ]; then
    echo "Building image with tag: $image_tag"
    docker build -t $image_tag -f ./init/Dockerfile-RenderPythonApps ./render-python-apps
fi    

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -d --name $container_name \
-v /Users/eric/nobackup:/mnt \
-v /Users/eric/tra/atPipeline/pipeline:/pipeline \
-v /Users/eric/tra/atPipeline/docker/render-python-apps:/usr/local/render-python-apps  \
-i -t $image_tag /bin/bash

echo "Done.."

# Second pass for rpa-master (to be removed when branches merged)
container_name="rpa-master"
image_tag="tottekarlsson/render-python-apps:master"

echo " ======== Building and starting Docker container with name: $container_name =============="

if [ $BUILD == "true" ]; then
    echo "Building image with tag: $image_tag"
    docker build -t $image_tag -f ./init/Dockerfile-RenderPythonApps ./render-python-apps
fi    

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -d --name $container_name \
-v /Users/eric/nobackup:/mnt \
-v /Users/eric/tra/atPipeline/pipeline:/pipeline \
-v /Users/eric/tra/atPipeline/docker/render-python-apps:/usr/local/render-python-apps  \
-i -t $image_tag /bin/bash

echo "Done.."
