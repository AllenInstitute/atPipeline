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

        self.name = "Pipeline mame is not defined"
        self.parameters = parameters
        self.pipeline_processes = []

    def get_name(self):
        return self.name

    def run(self):
        #Iterate through the pipeline
        for process in self.pipeline_processes:
            if process.check_if_done() == False or self.parameters.overwritedata == True:
                process.run()

                #Validate the result of the run
                res = process.validate()

                if res == False:
                    raise Exception("The '" + self.get_name()  + "' pipeline failed in pipeline step: " + process.get_name())
            else:
                logger.info("Skipping pipeline step: " + process.get_name())


    def append_pipeline_process(self, process : pp.PipelineProcess):
        self.pipeline_processes.append(process)


