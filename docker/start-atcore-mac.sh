#! /usr/bin/bash

#RENDER PYTHON APPS
image_tag="fcollman/render-python-apps"
container="renderapps_multchan"

echo " ======== Building and starting Docker container: $container =============="
echo "Building image with tag: $image_tag"
docker build -t $image_tag ./DockerInit/Dockerfile-RenderPythonApps-mac  

docker kill $container
docker rm $container

echo "Starting container: $container"
docker run -d --name $container \
-v /Users/synbio/Documents/data:/mnt/data/  \
-v /Users/synbio/ATExplorer/ThirdParty/atPipeline:/pipeline  \
-v /Users/synbio/ATExplorer/ThirdParty/Render-Python-Apps:/usr/local/render-python-apps  \
-i -t $image_tag /bin/bash

echo "Done.."