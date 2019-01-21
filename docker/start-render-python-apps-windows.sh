#! /usr/bin/bash
BUILD=${1:-false}
echo "Build flag is "$BUILD

#RENDER PYTHON APPS
image_tag="fcollman/render-python-apps"
container_name="rpa"

echo " ======== Building and starting Docker container with name: $container_name =============="

if [ $BUILD == "true" ]; then
    echo "Building image with tag: $image_tag"
    docker build -t $image_tag -f ./init/Dockerfile-RenderPythonApps ./Render-Python-Apps
fi    

echo "Killing container with name: $container_name"
docker kill $container_name
docker rm $container_name 

echo "Starting container with name: $container_name"
docker run -d --name $container_name \
-v e:/Documents/data:/mnt/  \
-v c:/pDisk/atExplorer/ThirdParty/atPipeline/pipeline:/pipeline  \
-v c:/pDisk/atExplorer/ThirdParty/Render-Python-Apps:/usr/local/render-python-apps  \
-i -t $image_tag /bin/bash

echo "Done.."