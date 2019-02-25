#! /usr/bin/bash

#Pull image from DOCKER HUB 
image_tag="atpipeline/atcore"
container_name="atcore"

echo "==== KILLING container: $container_name ===="
docker kill $container_name
docker rm $container_name 

echo " ==== STARTING container: $container_name ===="
docker run -d --name $container_name \
-v /c/data:/mnt/  \
-v $PWD/../pipeline:/pipeline  \
-v $PWD/render-python-apps:/shared/render-python-apps  \
-v $PWD/render-modules:/shared/render-modules  \
-i -t $image_tag /bin/bash

echo " ==== STARTED container: $container_name ===="
