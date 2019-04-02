import os
import logging
import json
import at_pipeline as atp
import at_pipeline_process as atpp
import at_stitching_pipeline
import at_utils as u
import posixpath

logger = logging.getLogger('atPipeline')

class RoughAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        p = self.parameters

        #Define the pipeline
        #self.stitchingPipeline                  at_stitching_pipeline.Stitch

        self.create_lowres_stacks                = CreateLowResStacks(p)
##        self.create_LR_tilepairs                 = CreateLowResTilePairs(p)
##        self.create_LR_pointmatches              = CreateLowResPointMatches(p)
##        self.create_rough_aligned_stacks         = CreateRoughAlignedStacks(p)
##        self.apply_lowres_to_highres             = ApplyLowResToHighRes(p)

        #We could store these in an array and pop them off one by one

    def run(self):
        atp.ATPipeline.run(self)

        #Create "sessionfolders"
        sessionFolders = []
        for ribbon in self.parameters.ribbons:
            #Create session folders
            for session in self.parameters.sessions:
              sessionFolders.append(os.path.join(self.parameters.projectDataFolder, self.parameters.projectDataFolder, "raw", "data", ribbon, session))

        self.create_lowres_stacks.run(sessionFolders)
##        self.create_LR_tilepairs.run(sessionFolders)
##        self.create_LR_pointmatches.run(sessionFolders)
##        self.create_rough_aligned_stacks.run(sessionFolders)
##        self.apply_lowres_to_highres.run(sessionFolders)
        return True

class CreateLowResStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateLowResStacks")

    def run(self, sessionFolders):
        p = self.paras

        for sessionFolder in sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
            firstRibbon = ribbon
            lastRibbon = int(p.ribbons[-1][6:])

            # output directories
            downsample_dir   = os.path.join(projectRoot, p.dataOutputFolder, "low_res")
            numsections_file = os.path.join(downsample_dir,                   "numsections")

            # Make sure output folder exist
            if os.path.isdir(downsample_dir) == False:
                os.mkdir(downsample_dir)

            # stacks
            input_stack  = "S%d_Stitched_Dropped"   %(session)
            output_stack = "S%d_LowRes"%(session)

            rp = p.renderProject

            # docker commands
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m renderapps.materialize.make_downsample_image_stack"
            cmd = cmd + " --render.host %s"                                %(rp.host)
            cmd = cmd + " --render.project %s"                             %(rp.projectName)
            cmd = cmd + " --render.owner %s"                               %(rp.owner)
            cmd = cmd + " --render.client_scripts %s"                      %(rp.clientScripts)
            cmd = cmd + " --render.memGB %s"                               %(rp.memGB)
            cmd = cmd + " --render.port %s"                                %(rp.hostPort)
            cmd = cmd + " --log_level %s"                                  %(rp.logLevel)
            cmd = cmd + " --input_stack %s"                                %(input_stack)
            cmd = cmd + " --output_stack %s"                               %(output_stack)
            cmd = cmd + " --image_directory %s"                            %(p.toMount(downsample_dir))
            cmd = cmd + " --pool_size %s"                                  %(p.atCoreThreads)
            cmd = cmd + " --scale %s"                                      %(p.downSampleScale)
            cmd = cmd + " --minZ %s"                                       %(firstRibbon*100)
            cmd = cmd + " --maxZ %s"                                       %((lastRibbon + 1)*100 - 1)
            cmd = cmd + " --numsectionsfile %s"                            %(p.toMount(numsections_file))

            # Run =============
            self.submit(cmd)

