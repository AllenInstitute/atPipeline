import os
import logging
import json
import at_pipeline as atp
import at_pipeline_process as atpp
from . import at_stitching_pipeline
import at_utils as u
import fileinput
from shutil import copyfile
import posixpath

logger = logging.getLogger('atPipeline')

class RoughAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.stitchingPipeline                   =  at_stitching_pipeline.Stitch(_paras)

        self.create_lowres_stacks                = CreateLowResStacks(_paras)
        self.create_lowres_tilepairs             = CreateLowResTilePairs(_paras)
        self.create_lowres_pointmatches          = CreateLowResPointMatches(_paras)
        self.create_rough_aligned_stacks         = CreateRoughAlignedStacks(_paras)
        self.apply_lowres_to_highres             = ApplyLowResToHighRes(_paras)

        #We could store these in an array and pop them off one by one

    def run(self):
        atp.ATPipeline.run(self)
        #Run any pre pipeline(s)
        self.stitchingPipeline.run()

        self.create_lowres_stacks.run()
        self.create_lowres_tilepairs.run()
        self.create_lowres_pointmatches.run()
        self.create_rough_aligned_stacks.run()
        self.apply_lowres_to_highres.run()
        return True

class CreateLowResStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateLowResStacks")

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:
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

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:
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

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:
            #Check which ribbon we are processing, and adjust section numbers accordingly
            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

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

    def run(self):
        super().run()
        p = self.paras
        rp  = p.renderProject

        for sessionFolder in self.sessionFolders:

            logger.info("Processing session folder: " + sessionFolder)
            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            #Output directories
            dataOutputFolder    = os.path.join(projectRoot, p.dataOutputFolder, "rough_aligned")
            input_json          = os.path.join(dataOutputFolder, "roughalignment_%s_%s_%d_%d.json"       %(ribbon, session, firstSection, lastSection))
            output_json         = os.path.join(dataOutputFolder, "output_roughalignment_%s_%s_%d_%d.json"%(ribbon, session, firstSection, lastSection))

            #stacks
            inputStack     = "S%d_LowRes"%(session)
            outputStack    = "S%d_RoughAligned_LowRes"%(session)

        	#point match collections
            lowresPmCollection = "%s_lowres_round"%rp.projectName

            with open(p.alignment_template) as json_data:
               ra = json.load(json_data)

            #Create folder if not exists
            if os.path.isdir(dataOutputFolder) == False:
                os.mkdir(dataOutputFolder)

            u.saveRoughAlignJSON(ra, input_json, rp, inputStack, outputStack, lowresPmCollection, firstSection, lastSection, p.toMount(dataOutputFolder))

            #Run docker command
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m rendermodules.solver.solve"
            cmd = cmd + " --input_json %s" %(p.toMount(input_json))
            cmd = cmd + " --output_json %s"%(p.toMount(output_json))
            self.submit(cmd)

class ApplyLowResToHighRes(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ApplyLowResToHighRes")

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            lowresStack             = "S%d_LowRes"%(session)

            inputStack              = "S%d_Stitched_Dropped"%(session)
            outputStack             = "S%d_RoughAligned"%(session)

            rp                      = p.renderProject

            roughalign_ts_dir = os.path.join(projectRoot, p.dataOutputFolder, "rough_aligned_tilespecs")

            # Make sure output folder exist
            if os.path.isdir(roughalign_ts_dir) == False:
                os.mkdir(roughalign_ts_dir)

            #Put this in ini file later on..
            scale = 0.05

            #Run docker command
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m renderapps.rough_align.ApplyLowRes2HighRes"
            cmd = cmd + " --render.host %s"                %(rp.host)
            cmd = cmd + " --render.owner %s "              %(rp.owner)
            cmd = cmd + " --render.project %s"             %(rp.projectName)
            cmd = cmd + " --render.client_scripts %s"      %(rp.clientScripts)
            cmd = cmd + " --render.port %d"                %(rp.hostPort)
            cmd = cmd + " --render.memGB %s"               %(rp.memGB)
            cmd = cmd + " --pool_size %d"                  %(p.atCoreThreads)
            cmd = cmd + " --tilespec_directory %s"         %(p.toMount(roughalign_ts_dir))
            cmd = cmd + " --scale %s"                      %(p.downSampleScale)
            cmd = cmd + " --input_stack %s"                %(inputStack)
            cmd = cmd + " --lowres_stack %s"               %(lowresStack)
            cmd = cmd + " --prealigned_stack %s"           %(inputStack)
            cmd = cmd + " --output_stack %s"     		   %(outputStack)

            #TODO: get the Z's right..
            #firstribbon             = p.firstRibbon
            #lastribbon              = p.lastRibbon

            cmd = cmd + " --minZ 0"#%d"                  %(p.firstSection*100)
            cmd = cmd + " --maxZ 500"#%d"                  %(p.lastSection*100)
            #cmd = cmd + " --minZ %d --maxZ %d "       %(firstribbon*100, (lastribbon+1) * 100)

            self.submit(cmd)