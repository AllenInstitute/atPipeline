The start of a RESTful server for running the Array Tomography Pipeline.

The docker image is based on the 'atcore' image, which contains all of the command line tools used to run the pipeline.

Usage:
    docker build . -t atpipeline/atserver:dev
    docker run --init --rm -p 5050:5050 atpipeline/atserver:dev
