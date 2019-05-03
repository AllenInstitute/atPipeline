#! /bin/bash
if [ "$1" == "" ]; then
    echo "Supply the tag for the image to build"
    exit 1
fi

imagetag=$1
base_image_tag=0.2
echo docker build --build-arg BASE_TAG=$base_image_tag -t atpipeline/clang:$imagetag -t atpipeline/clang:latest -f ClangDockerFile.txt .
docker build --build-arg BASE_TAG=$base_image_tag -t atpipeline/clang:$imagetag -t atpipeline/clang:latest -f ClangDockerFile.txt .
