# atPipeline

Pipeline code for processing Array Tomography (AT) data, built as part of [Stephen Smith](https://alleninstitute.org/what-we-do/brain-science/about/team/staff-profiles/stephen-j-smith/) group at the (Allen Institute)[https://alleninstitute.org].

The first stages of the pipeline code are specific to data collected within the lab, but most of the steps could be modified for use on similar data.

## Documentation
* [Setup instructions](SETUP.md)
* [Usage instructions](USAGE.md)
* [Instructions to rebuild docker containers](docker/README.md)
  * _Optional_, containers can be pulled from [docker hub](https://hub.docker.com/orgs/atpipeline).
* [Export data from render](EXPORT.md)


## Requirements

The AT Pipeline requiremes Python >= 3.4.

## Installation

To install in developer mode (e.g., install via symlink)
```console
% pip install git+https://github.com/fcollman/render-python
% pip install -e .
```

_TODO: Copy templates/*.template to /usr/local/etc or alternate config path._

## Start the backend (atbackend)

The backend can be run with ```atbackend <args>``` or ```python -m atpipeline.atbackend <args>```.

## Run the pipeline (atfrontend)

The backend can be run with ```atcore <args>``` or ```python -m atpipeline.atcore <args>```.

## Level of support

We are planning on occasional updating this tool with no fixed schedule. Community involvement is encouraged through both issues and pull requests.

## Contributors
