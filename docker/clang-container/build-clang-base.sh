#! /bin/bash

if [ "$1" == "" ]; then
    echo "Supply the tag for the image to build"
    exit 1
fi

imagetag=$1

echo docker build -t atpipeline/clang-base-image:$imagetag -f ClangBaseDockerFile.txt . 
docker build -t atpipeline/clang-base-image:$imagetag -f ClangBaseDockerFile.txt . 
