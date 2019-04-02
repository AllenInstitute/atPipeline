#! /bin/bash
if [ "$1" == "" ]; then
    echo "Supply the tag for the image to build"
    exit 1
fi

imagetag=$1

echo docker build --build-arg BASE_TAG=$imagetag -t atpipeline/clang:$imagetag -t atpipeline/clang:$imagetag -f ClangDockerFile.txt .
docker build --build-arg BASE_TAG=$imagetag -t atpipeline/clang:$imagetag -t atpipeline/clang:$imagetag -f ClangDockerFile.txt .
