#The ATPipeline class
import logging
import os
import docker
import subprocess
import json
from . import at_system_config as c
from . import at_utils as u

logger = logging.getLogger('atPipeline')

class ATPipeline:
    def __init__(self, parameters : c.ATSystemConfig):
        self.parameters = parameters

        dockerClient = docker.from_env()
        atcore = dockerClient.containers.get("atcore")
        render = dockerClient.containers.get("default_render_1")

        if render.status != "running":
            raise ValueError("The Render docker container is not running!")

        if atcore.status != "running":
            raise ValueError("The atcore docker container is not running!")

    def run(self):
        pass



