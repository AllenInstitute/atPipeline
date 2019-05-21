import os
import logging
import json
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from .. import at_utils as u

#Import pipelinesteps.. put these steps in 'categorized' pipeline steps files later on?
from . import at_stitching_pipeline as ps
import posixpath

logger = logging.getLogger('atPipeline')

class SingleTileData(atp.ATPipeline):
    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.append_pipeline_process(ps.CreateStateTables(_paras))
        self.append_pipeline_process(ps.CreateRawDataRenderStacks(_paras))
        self.append_pipeline_process(ps.CreateMedianFiles(_paras))
        self.append_pipeline_process(ps.CreateFlatFieldCorrectedData(_paras))
        #self.append_pipeline_process(CreateStitchedSections(_paras))
        #self.append_pipeline_process(DropStitchingMistakes(_paras))

    def run(self):
        atp.ATPipeline.run(self)

        #Iterate through the pipeline
        for process in self.pipeline_processes:

            if process.check_if_done() == False:
                process.run()

                #Validate the result of the run
                res = process.validate()

                if res == False:
                    logger.info("Failed in pipelinestep" + process.get_name())
                    return False
            else:
                logger.info("Skipping pipeline step: " + process.get_name())

        return True



