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

        rp = p.renderProject

        reference_session = 1
        output_dir = os.path.join(p.absoluteDataOutputFolder, "fine_registration")
        if os.path.isdir(output_dir) == False:
            os.mkdir(output_dir)

        print(self.sessionFolders)
        for sessionFolder in self.sessionFolders:
            try:
                logger.info("=========== Working on fine registration for: " + sessionFolder + " ===============")

                #Check which ribbon we are processing, and adjust section numbers accordingly
                ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
                firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbon)
                [project_root, ribbon, session] = u.parse_session_folder(sessionFolder)

                if session == reference_session:
                    logger.info("Skipping session %d (reference session)" % session)
                    continue
                else:
                    logger.info("Processing session: " + str(session))
                    prealigned_stack = "S1_Stitched"
                    postaligned_stack = "S1_FineAligned"
                    source_stack = "S%d_Stitched" %(int(session))
                    output_stack = "S%d_FineAligned_Registered"%(int(session))

                    cmd = "docker exec " + p.atCoreContainer
                    cmd = cmd + " /opt/conda/bin/python -m renderapps.registration.apply_alignment_transform_from_registered_stack"
                    cmd = cmd + " --render.host %s"                 %(rp.host)
                    cmd = cmd + " --render.owner %s "               %(rp.owner)
                    cmd = cmd + " --render.project %s"              %(rp.project_name)
                    cmd = cmd + " --render.client_scripts %s"       %(rp.clientScripts)
                    cmd = cmd + " --render.port %d"                 %(rp.hostPort)
                    cmd = cmd + " --render.memGB %s"                %(rp.memGB)

                    cmd = cmd + " --prealigned_stack %s"            %(prealigned_stack)
                    cmd = cmd + " --postaligned_stack %s"           %(postaligned_stack)
                    cmd = cmd + " --source_stack %s"                %(source_stack)
                    cmd = cmd + " --output_stack %s"                %(output_stack)
                    cmd = cmd + " --pool_size %d"                   %(4)
                    cmd = cmd + " --diffZ %s"                       %("True")

                    self.submit(cmd)
            except:
                raise

        return False

