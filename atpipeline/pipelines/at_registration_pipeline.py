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
        self.append_pipeline_process(RegisterSessionsProcessJava(_paras))

    def run(self):
        atp.ATPipeline.run(self)


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

class RegisterSessionsProcessJava(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "RegisterSessionsProcess")

    def validate(self):
        super().validate()

    def run(self):
        super().run()

        try:
            p = self.paras
            rp = p.renderProject
            registrationtemplate = "templates/registration.json"


            jsonOutputFolder  = os.path.join(p.absoluteDataOutputFolder, "registration")

            # Make sure that the output folder exist
            if os.path.isdir(jsonOutputFolder) == False:
                os.mkdir(jsonOutputFolder)


            #stacks
            #session = 2
            #reference_stack     = "S1_Stitched"
            #stitched_stack      = "S%d_Stitched"%(int(session))
            #outputStack         = "S%d_Registered"%(int(session))

            #Loop over sections?
            #sectnum = 0
            #ribbon = 4
            #z = ribbon*100+sectnum

            #This is the registration input (json) file
            #inputJSON = os.path.join(jsonOutputFolder, "registration_%s_%s_%d.json"%(ribbon, session, sectnum))

            #create input file for registration
            #with open(p.registration_template) as json_data:
            #    t = json.load(json_data)

            #u.saveRegistrationJSON(t, inputJSON, rp.host, rp.owner, rp.project_name, stitched_stack, reference_stack, outputStack, z)


            output_dir = os.path.join(p.absoluteDataOutputFolder, "registration")
            for sessionDir in p.sessions:
                session = int(sessionDir[7:])
                logger.info("Processing session: " + str(session))

                reference_stack     = "S1_FineAligned"
                stitched_stack      = "S%d_FineAligned"%(int(session))
                outputStack         = "S%d_FineAligned_registered"%(int(session))

                if session == 1:
                    logger.info("Skipping session %d (reference session)" % session)
                if session > 1:
                    for section in range(p.firstSection, p.lastSection + 1):
                        cmd = "docker exec " + p.atCoreContainer
                        cmd = cmd + " /opt/conda/bin/python -m renderapps.registration.calc_registration"
                        cmd = cmd + " --render.host %s"                 %(rp.host)
                        cmd = cmd + " --render.owner %s "               %(rp.owner)
                        cmd = cmd + " --render.project %s"              %(rp.project_name)
                        cmd = cmd + " --render.client_scripts %s"       %(rp.clientScripts)
                        cmd = cmd + " --render.port %d"                 %(rp.hostPort)
                        cmd = cmd + " --render.memGB %s"                %(rp.memGB)
                        cmd = cmd + " --stack %s"                       %(stitched_stack)
                        cmd = cmd + " --referenceStack %s"              %(reference_stack)
                        cmd = cmd + " --outputStack %s"     		    %(outputStack)
                        cmd = cmd + " --section %d"                     %(section)
                        cmd = cmd + " --output_dir %s"                  %(output_dir)
                        # Run =============
                        self.submit(cmd)
            return False
        except:
            raise



