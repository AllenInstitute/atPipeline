import os
import logging
import json
import fileinput
from shutil import copyfile
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_registration_pipeline
from . import at_rough_align_pipeline
from .. import at_utils as u


logger = logging.getLogger('atPipeline')

class RoughAlignRegistration(atp.ATPipeline):
    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.roughAlignPipeline = at_rough_align_pipeline.RoughAlign(_paras)
        self.registrationPipeline = at_registration_pipeline.RegisterSessions(_paras)
        self.append_pipeline_process(ApplyLowToZighResRegistered(_paras))

    def run(self):
        #Run any pre pipeline(s)
        self.registrationPipeline.run()
        self.roughAlignPipeline.run()

        atp.ATPipeline.run(self)
        
        return True

class ApplyLowToZighResRegistered(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ApplyLowToZighResRegistered")

##    def check_if_done(self):
##        pass

    def run(self):
        super().run()
        p = self.paras

        rp = p.renderProject

        reference_session = 1
        output_dir = os.path.join(p.absoluteDataOutputFolder, "rough_registration")
        if os.path.isdir(output_dir) == False:
            os.mkdir(output_dir)

        print(self.sessionFolders)
        for sessionFolder in self.sessionFolders:
            try:
                logger.info("=========== Working on rough aligned registration for: " + sessionFolder + " ===============")

                #Check which ribbon we are processing, and adjust section numbers accordingly
                ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
                firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbon)
                [project_root, ribbon, session] = u.parse_session_folder(sessionFolder)

                if session == reference_session:
                    logger.info("Skipping session %d (reference session)" % session)
                    continue
                else:
                    logger.info("Processing session: " + str(session))
                    lowresStack = "S%d_RoughAligned_LowRes"%(reference_session)
                    inputStack = "S%d_Stitched_Dropped_Registered"%(session)
                    outputStack = "S%d_RoughAligned_Registered"%(session)

                    #Run docker command
                    cmd =       "/opt/conda/bin/python -m renderapps.rough_align.ApplyLowRes2HighRes"
                    cmd = cmd + " --render.host %s"                %(rp.host)
                    cmd = cmd + " --render.owner %s "              %(rp.owner)
                    cmd = cmd + " --render.project %s"             %(rp.project_name)
                    cmd = cmd + " --render.client_scripts %s"      %(rp.clientScripts)
                    cmd = cmd + " --render.port %d"                %(rp.hostPort)
                    cmd = cmd + " --render.memGB %s"               %(rp.memGB)
                    cmd = cmd + " --pool_size %s"                  %(p.GENERAL['AT_CORE_THREADS'])
                    cmd = cmd + " --tilespec_directory %s"         %(p.toMount(output_dir))
                    cmd = cmd + " --scale %s"                      %(p.CREATE_LOWRES_STACKS['SCALE'])
                    cmd = cmd + " --input_stack %s"                %(inputStack)
                    cmd = cmd + " --lowres_stack %s"               %(lowresStack)
                    cmd = cmd + " --prealigned_stack %s"           %(inputStack)
                    cmd = cmd + " --output_stack %s"     		   %(outputStack)


                    #cmd = cmd + " --minZ 0"#%d"                  %(p.firstSection*100)
                    #cmd = cmd + " --maxZ 5000"#%d"                  %(p.lastSection*100)
                    first_ribbon = int(p.ribbons[0][6:])
                    last_ribbon  = int(p.ribbons[-1][6:])

                    cmd = cmd + " --minZ %d --maxZ %d"       %(first_ribbon*100, (last_ribbon+1) * 100)

                    self.submit_atcore(cmd)
            except:
                raise

            logger.info("Combining registered volumes into a single stack")
            # TODO: Do we need to do this? Can we just apply the low-res transformations to the previously merged stack?

            stack_merge_list = []
            merged_stack = "S%d_RoughAligned_Registered_Merged"%(int(reference_session))
            for sessionFolder in self.sessionFolders:
                 [project_root, ribbon, session] = u.parse_session_folder(sessionFolder)
                 if session == reference_session:
                     stack_to_merge = "S%d_RoughAligned"%(int(session))
                 else:
                     stack_to_merge = "S%d_RoughAligned_Registered"%(int(session))
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

        return True

