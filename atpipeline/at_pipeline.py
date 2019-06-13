#The ATPipeline class
import logging
import os
import docker
import subprocess
import json
from . import at_system_config as c
from . import at_utils as u
from . import at_pipeline_process as pp

logger = logging.getLogger('atPipeline')

class ATPipeline:
    def __init__(self, parameters : c.ATSystemConfig):
        self.parameters = parameters

        dockerClient = docker.from_env()
        atcore = dockerClient.containers.get(self.parameters.atcore_ctr_name)
        render = dockerClient.containers.get("default_render_1")

        if render.status != "running":
            raise ValueError("The Render docker container is not running!")

        if atcore.status != "running":
            raise ValueError("The atcore docker container is not running!")

        self.pipeline_processes = []

    def run(self):
        #Iterate through the pipeline
        for process in self.pipeline_processes:
            if process.check_if_done() == False or self.parameters.overwritedata == True:
                process.run()

                #Validate the result of the run
                res = process.validate()

                if res == False:
                    logger.info("Failed in pipelinestep" + process.get_name())
                    return False
            else:
                logger.info("Skipping pipeline step: " + process.get_name())


    def append_pipeline_process(self, process : pp.PipelineProcess):
        self.pipeline_processes.append(process)


