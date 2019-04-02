import os
import logging
import json
import at_pipeline as atp
import at_pipeline_process as atpp
import at_stitching_pipeline
import at_utils as u
import fileinput
from shutil import copyfile
import posixpath

logger = logging.getLogger('atPipeline')

class RoughAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        p = self.parameters

        #Define the pipeline
        #self.stitchingPipeline                  at_stitching_pipeline.Stitch

        self.create_lowres_stacks                = CreateLowResStacks(p)
        self.create_lowres_tilepairs             = CreateLowResTilePairs(p)
        self.create_lowres_pointmatches          = CreateLowResPointMatches(p)
        self.create_rough_aligned_stacks         = CreateRoughAlignedStacks(p)
        self.apply_lowres_to_highres             = ApplyLowResToHighRes(p)

        #We could store these in an array and pop them off one by one

    def run(self):
        atp.ATPipeline.run(self)

        #Create "sessionfolders"
        sessionFolders = []
        for ribbon in self.parameters.ribbons:
            #Create session folders
            for session in self.parameters.sessions:
              sessionFolders.append(os.path.join(self.parameters.projectDataFolder, self.parameters.projectDataFolder, "raw", "data", ribbon, session))

        #self.create_lowres_stacks.run(sessionFolders)
##        self.create_lowres_tilepairs.run(sessionFolders)
        self.create_lowres_pointmatches.run(sessionFolders)
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


#Note, this seem to require at least two sections to work which makes sense, so tell the user that
class CreateLowResTilePairs(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateLowResTilePairs")

    def run(self, sessionFolders):
        p = self.paras

        for sessionFolder in sessionFolders:
            #Check which ribbon we are processing, and adjust section numbers accordingly
            ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbon)

            logger.info("Processing session folder: " + sessionFolder)
            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
            inputStack = "S%d_LowRes"%(session)

            rp      = p.renderProject
            jsondir = os.path.join(projectRoot, p.dataOutputFolder, "lowres_tilepairfiles")

            # Make sure output folder exist
            if os.path.isdir(jsondir) == False:
                os.mkdir(jsondir)

            jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch.json"     %(p.zNeighborDistance, firstSection, lastSection))

            #Run the TilePairClient
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.0-SNAPSHOT-standalone.jar"
            cmd = cmd + " org.janelia.render.client.TilePairClient"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --owner %s"							    %(rp.owner)
            cmd = cmd + " --project %s"                             %(rp.projectName)
            cmd = cmd + " --stack %s"                               %(inputStack)
            cmd = cmd + " --minZ %d"                                %(firstSection)
            cmd = cmd + " --maxZ %d"                                %(lastSection)
            cmd = cmd + " --toJson %s"                              %(p.toMount(jsonfile))
            cmd = cmd + " --excludeCornerNeighbors %s"              %(p.excludeCornerNeighbors)
            cmd = cmd + " --excludeSameSectionNeighbors %s"         %(p.excludeSameSectionNeighbors)
            cmd = cmd + " --zNeighborDistance %s"                   %(p.zNeighborDistance)
            cmd = cmd + " --xyNeighborFactor %s"                    %(p.xyNeighborFactor)

            #Run =============
            self.submit(cmd)

            #Prepare json file for the SIFTPointMatch Client
            jsonfileedit      = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch-EDIT.json"%(p.zNeighborDistance, firstSection, lastSection))
            copyfile(jsonfile, jsonfileedit)

            for line in fileinput.input(jsonfileedit, inplace=True):
                print(line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")


class CreateLowResPointMatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateLowResPointMatches")

    def run(self, sessionFolders):
        p = self.paras
        for sessionFolder in sessionFolders:
            #Check which ribbon we are processing, and adjust section numbers accordingly
            ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbon)


            if firstSection == -1: #This just means that no section in the current ribbon are selected for processing
                continue

            logger.info("Processing session folder: " + sessionFolder)
            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            rp     = p.renderProject

            #output directories
            downsample_dir   = os.path.join(projectRoot, p.dataOutputFolder, "low_res")

            jsondir  = os.path.join(projectRoot, p.dataOutputFolder, "lowres_tilepairfiles")
            jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch-EDIT.json"     %(p.zNeighborDistance, firstSection, lastSection))

            #SIFT Point Match Client
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " /usr/spark-2.0.2/bin/spark-submit"
            cmd = cmd + " --conf spark.default.parallelism=4750"
            cmd = cmd + " --driver-memory %s"                       %(p.SPARK['driverMemory'])
            cmd = cmd + " --executor-memory %s"                     %(p.SPARK['executorMemory'])
            cmd = cmd + " --executor-cores %s"                      %(p.SPARK['executorCores'])

            cmd = cmd + " --class org.janelia.render.client.spark.SIFTPointMatchClient"
            cmd = cmd + " --name PointMatchFull"
            cmd = cmd + " --master local[*] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.1.0-SNAPSHOT-standalone.jar"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --collection %s_lowres_round"             %(rp.projectName)
            cmd = cmd + " --owner %s"                               %(rp.owner)
            cmd = cmd + " --pairJson %s"                            %(p.toMount(jsonfile))
            cmd = cmd + " --renderWithFilter true"
            cmd = cmd + " --maxFeatureCacheGb 40"
            cmd = cmd + " --matchModelType RIGID"
            cmd = cmd + " --matchMinNumInliers 15"
            #cmd = cmd + " --matchMaxEpsilon 15.0"
            #cmd = cmd + " --matchMaxTrust 1.0"

            cmd = cmd + " --SIFTmaxScale 0.85"
            cmd = cmd + " --SIFTminScale 0.7"
            cmd = cmd + " --SIFTsteps 5"
            cmd = cmd + " --renderScale 1.0"
            cmd = cmd + " --matchRod 0.5"
            #cmd = cmd + " --matchFilter CONSENSUS_SETS"

            #Run =============
            self.submit(cmd)


class CreateRoughAlignedStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateRoughAlignedStacks")

    def run(self, sessionFolders):
        p = self.paras

class ApplyLowResToHighRes(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ApplyLowResToHighRes")

    def run(self, sessionFolders):
        p = self.paras
