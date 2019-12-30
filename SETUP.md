# Setup instructions

## Requirements

* [docker](https://docs.docker.com/install/)
* [docker-compose](https://docs.docker.com/compose/) (included with Docker on Mac and Windows)
* python 3.5, 3.6 or 3.7

## Installation

Create and activate a new python virtual environment:
```bash
python3 -m venv ATENV
source ATENV/bin/activate
```

Install this package from the top level directory:
```bash
pip install .
```

## Copy config files

The following config files  must be copied into `/usr/local/etc`. An alternate path can be used by setting the `AT_SYSTEM_CONFIG_FOLDER` environment variable or using the `--configfolder` flag with each command.

```bash
cp config/at-docker-compose.yml.template /usr/local/etc/at-docker-compose.yml
cp config/at-vizrelay-config.json.template /usr/local/etc/at-vizrelay-config.json
cp config/at-data-processing-config.ini.template /usr/local/etc/at-data-processing-config.ini
cp config/at-system-config.ini.template /usr/local/etc/at-system-config.ini
```

## Edit config files

### at-docker-compose.yml
`at-docker-compose.yml` specifies the configuration for services started by docker-compose.

* The default `JAVA_OPTIONS` for render will allocate 10G of memory for render. Adjust down on machines with less memory.
* Specify a volume mount for render to access data. An example is included for both Windows and Linux, e.g., `- /data:/data`.  Repeat for each path to volumes with data to be read. 
*Required*

Ports for the various services can be adjusted here as well.

### at-vizrelay-config.json

The `base_url` section should be replaced with a valid URL for the neuroglancer deployment, e.g., `http://your.hostname.here:8001`. (The default, 'http://localhost:8001', will work if you do not need access from other machines on the network.)

### at-data-processing-config.ini
`at-data-processing-config.ini` sets parameters used for each of the processing stages. Individual parameters can be overwritten at run-time with the "--define SECTION.item=value" flag.

The `MAX_FEATURE_CACHE_GB` sections of `LOWRES_POINTMATCHES` and `CREATE_HR_POINTMATCHES` will need to be reduced on low memory systems (e.g. < 16GB>).

* `USE_DOCKER_USER_FLAG`: Use the `--user` flag to run `atcore` as a non-root user. Must be `no` on Windows.
* `RUN_ATCORE_AS_CALLING_USER`: If `yes`, run as the same user running thea `atcore` command. If no, run as the user specified in `RUN_ATCORE_AS_USER`.
* `RUN_ATCORE_AS_CALLING_GROUP`: If `yes`, run as the same user running thea `atcore` command. If no, run as the user specified in `RUN_ATCORE_AS_GROUP`.

### at-system-config.ini

`at-system-config.ini` provides settings for the backend services.

* `DATA_ROOTS`: mapping of mounts between the host system and the docker container. This should reflect the paths set in `at-docker-compose.yml`. These are used for the volume mounts of the `atcore` container.
* `HOST_MEMORY`: the amount of memory available (in GB). Up to 50% will be used for data processing.
* `HOST_NUMBER_OF_CORES`: number of distinct cores to use for tasks.
* `AT_CORE_THREADS`: number of threads for multi-threaded tasks.
* `JSON_TEMPLATES_FOLDER`L full path to the templates directory in the checked out code
* `RENDER_HOST`: complete hostname of the render server. *Note:* `localhost` will not work between containers. On the mac, you can use `host.docker.internal`.

## Start the backend

The following command will start the backend:

```bash
atbackend --startall
```

Check the status:
```bash
atbackend --status
```

...which should report 5 running containers:
```
12:34:29 - INFO - atbackend :: ============ Managing the atBackend =============
12:34:29 - INFO - at_docker_manager :: Container: default_atcore : running
12:34:29 - INFO - at_docker_manager :: Container: default_render_1 : running
12:34:29 - INFO - at_docker_manager :: Container: default_vizrelay_1 : running
12:34:29 - INFO - at_docker_manager :: Container: default_neuroglancer_1 : running
12:34:29 - INFO - at_docker_manager :: Container: default_mongo_1 : running
```

Backend services can be stopped with:
```bash
atbackend --killall 
```
