import os
import logging
import json
import fileinput
from shutil import copyfile
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_rough_align_pipeline
from .. import at_utils as u


logger = logging.getLogger('atPipeline')

class RegisterSessions(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.roughAlignPipeline = at_rough_align_pipeline.RoughAlign(_paras)
        self.append_pipeline_process(RegisterSessionsProcess(_paras))

    def run(self):
        atp.ATPipeline.run(self)

        #Run any pre pipeline(s)
        self.roughAlignPipeline.run()

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

class RegisterSessionsProcess(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "RegisterSessionsProcess")

    def validate(self):
        super().validate()

    def run(self):
        super().run()
        p = self.paras

        rp = p.renderProject
        # registrationtemplate = "templates/registration.json"

        reference_session = 1
        output_dir = os.path.join(p.absoluteDataOutputFolder, "registration")
        if os.path.isdir(output_dir) == False:
            os.mkdir(output_dir)

        print(self.sessionFolders)
        for sessionFolder in self.sessionFolders:
            try:
                logger.info("=========== Working on registrations for: " + sessionFolder + " ===============")

                #Check which ribbon we are processing, and adjust section numbers accordingly
                ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
                firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbon)
                [project_root, ribbon, session] = u.parse_session_folder(sessionFolder)

                if session == reference_session:
                    logger.info("Skipping session %d (reference session)" % session)
                    continue
                else:
                    logger.info("Processing session: " + str(session))
                    reference_stack     = "S1_Stitched"
                    reference_stack_channel   = "DAPI_1"
                    stitched_stack      = "S%d_Stitched" %(int(session))
                    stitched_stack_channel = "DAPI_%d" % (int(session))
                    outputStack         = "S%d_Registered"%(int(session))
                    for sectnum in range(firstSection, lastSection + 1):
                        z = ribbon*100+sectnum

                        cmd = "docker exec " + p.atCoreContainer
                        cmd = cmd + " /opt/conda/bin/python -m renderapps.registration.calc_registration"
                        cmd = cmd + " --render.host %s"                 %(rp.host)
                        cmd = cmd + " --render.owner %s "               %(rp.owner)
                        cmd = cmd + " --render.project %s"              %(rp.project_name)
                        cmd = cmd + " --render.client_scripts %s"       %(rp.clientScripts)
                        cmd = cmd + " --render.port %d"                 %(rp.hostPort)
                        cmd = cmd + " --render.memGB %s"                %(rp.memGB)
                        cmd = cmd + " --stack %s"                       %(stitched_stack)
                        cmd = cmd + " --stackChannel %s"                %(stitched_stack_channel)
                        cmd = cmd + " --referenceStack %s"              %(reference_stack)
                        cmd = cmd + " --referenceStackChannel %s"       %(reference_stack_channel)
                        cmd = cmd + " --outputStack %s"     		    %(outputStack)
                        cmd = cmd + " --section %d"                     %(z)
                        cmd = cmd + " --output_dir %s"                  %(output_dir)
                        cmd = cmd + " --grossRefStack %s"               %("tempGrossStack1")
                        cmd = cmd + " --grossStack %s"                  %("tempGrossStack2")
                        cmd = cmd + " --filter %d"                      %(1)
                        cmd = cmd + " --matchcollection %s"             %("S1_S%d_matches" % session)
                        cmd = cmd + " --pool_size %d"                   %(1)
                        cmd = cmd + " --scale %f"                       %(0.25)
                        self.submit(cmd)
            except:
                raise
        return True
