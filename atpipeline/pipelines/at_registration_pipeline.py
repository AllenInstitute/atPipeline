import os
import logging
import json
import fileinput
from shutil import copyfile
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_rough_align_pipeline
from . import at_stitching_pipeline
from .. import at_utils as u


logger = logging.getLogger('atPipeline')

class RegisterSessions(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)
        self.name = "register"

        #Define the pipeline
        self.stitchingPipeline = at_stitching_pipeline.Stitch(_paras)
        self.append_pipeline_process(RegisterSessionsProcess(_paras))

    def run(self):
        #Run any pre pipeline(s)
        self.stitchingPipeline.run()
        atp.ATPipeline.run(self)

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
                    reference_stack     = "S%d_Stitched_Dropped" % int(reference_session)
                    reference_stack_channel   = "%s_%d" % (p.referenceChannelRegistration, int(reference_session))
                    stitched_stack      = "S%d_Stitched_Dropped" %(int(session))
                    stitched_stack_channel = "%s_%d" % (p.referenceChannelRegistration, int(session))
                    outputStack         = "S%d_Stitched_Dropped_Registered"%(int(session))
                    for sectnum in range(firstSection, lastSection + 1):
                        z = ribbon*100+sectnum

                        cmd =       " /opt/conda/bin/python -m renderapps.registration.calc_registration"
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
                        cmd = cmd + " --grossRefStack %s"               %("%s_tempGrossStack1" % rp.project_name)
                        cmd = cmd + " --grossStack %s"                  %("%s_tempGrossStack2" % rp.project_name)
                        cmd = cmd + " --filter %d"                      %(1)
                        cmd = cmd + " --matchcollection %s"             %("%s_S1_S%d_matches" % (rp.project_name, session))
                        cmd = cmd + " --pool_size %d"                   %(1)
                        cmd = cmd + " --scale %f"                       %(0.25)
                        self.submit_atcore(cmd)
            except:
                raise

        logger.info("Combining registered volumes into a single stack")
        stack_merge_list = []
        merged_stack = "S%d_Stitched_Dropped_Registered_Merged"%(int(reference_session))
        for sessionFolder in self.sessionFolders:
            [project_root, ribbon, session] = u.parse_session_folder(sessionFolder)
            if session == reference_session:
                stack_to_merge = "S%d_Stitched_Dropped"%(int(session))
            else:
                stack_to_merge = "S%d_Stitched_Dropped_Registered"%(int(session))
            stack_merge_list.append(stack_to_merge)

        print("Merging %s" % stack_merge_list)

        cmd =       " /opt/conda/bin/python -m renderapps.stack.merge_stacks"
        cmd = cmd + " --render.host %s"                 %(rp.host)
        cmd = cmd + " --render.owner %s "               %(rp.owner)
        cmd = cmd + " --render.project %s"              %(rp.project_name)
        cmd = cmd + " --render.client_scripts %s"       %(rp.clientScripts)
        cmd = cmd + " --render.port %d"                 %(rp.hostPort)
        cmd = cmd + " --render.memGB %s"                %(rp.memGB)
        cmd = cmd + " --output_stack %s"                %(merged_stack)
        cmd = cmd + " --stacks %s"                      %(' '.join(stack_merge_list))

        self.submit_atcore(cmd)
