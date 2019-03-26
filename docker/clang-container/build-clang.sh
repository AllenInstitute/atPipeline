#! /bin/bash
if [ "$1" == "" ]; then
    echo "Supply the tag for the image to build"
    exit 1
fi

imagetag=$1

docker build --no-cache -t atpipeline/clang:$imagetag -t atpipeline/clang:latest -f ClangDockerFile.txt .