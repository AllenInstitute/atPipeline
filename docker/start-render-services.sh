#!/usr/bin/env bash
DOCKER_COMPOSE=""
if [[ "$OSTYPE" == "linux-gnu" ]]; then
    DOCKER_COMPOSE=./init/docker-compose-linux.yml
elif [[ "$OSTYPE" == "darwin"* ]]; then
    DOCKER_COMPOSE=./init/docker-compose-mac.yml
elif [[ "$OSTYPE" == "cygwin" ]]; then
    DOCKER_COMPOSE=./init/docker-compose-windows.yml
else
    DOCKER_COMPOSE=./init/docker-compose-windows.yml
fi

echo "Starting RenderServices using DockerCompose file: $DOCKER_COMPOSE"
docker-compose -f $DOCKER_COMPOSE up -d
