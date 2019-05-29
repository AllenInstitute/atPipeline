import os
import logging
import json
import fileinput
from shutil import copyfile
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_registration_pipeline
from . import at_fine_align_pipeline
from .. import at_utils as u


logger = logging.getLogger('atPipeline')

class FineAlignRegistration(atp.ATPipeline):
    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.registrationPipeline = at_registration_pipeline.RegisterSessions(_paras)
        self.finealignPipeline = at_fine_align_pipeline.FineAlign(_paras)
        self.append_pipeline_process(FineAlignRegistrationProcess(_paras))

    def run(self):
        atp.ATPipeline.run(self)

        #Run any pre pipeline(s)
        self.registrationPipeline.run()
        self.finealignPipeline.run()

        #Iterate through the pipeline
        for process in self.pipeline_processes:

            if process.check_if_done() == False:
                if process.run() == False:
                    logger.info("Failed in pipelinestep: " + process.get_name())
                    return False

                #Validate the result of the run
                res = process.validate()

                if res == False:
                    logger.info("Failed validating pipeline step: " + process.get_name())
                    return False
            else:
                logger.info("Skipping pipeline step: " + process.get_name())


        return True

class FineAlignRegistrationProcess(atpp.PipelineProcess):
    def __init__(self, _paras):
        super().__init__(_paras, "FineAlignRegistrationProcess")

    def validate(self):
        super().validate()

    def run(self):
        super().run()
        p = self.paras
        return False

