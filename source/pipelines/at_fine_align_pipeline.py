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

class FineAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        p = self.parameters

        #Define the pipeline
        #self.stitchingPipeline                  at_stitching_pipeline.Stitch
        self.consolidateRoughAlignedStackTransforms = ConsolidateRoughAlignedStackTransforms
        self.create_2D_pointmatches                 = Create_2D_pointmatches
        self.create_HR_tilepairs                    = Create_HR_tilepairs
        self.create_HR_pointmatches                 = Create_HR_pointmatches
        self.create_fine_aligned_stacks             = Create_fine_aligned_stacks

    def run(self):
        atp.ATPipeline.run(self)

        #Create "sessionfolders"
        sessionFolders = []
        for ribbon in self.parameters.ribbons:
            #Create session folders
            for session in self.parameters.sessions:
              sessionFolders.append(os.path.join(self.parameters.projectDataFolder, self.parameters.projectDataFolder, "raw", "data", ribbon, session))

        self.consolidateRoughAlignedStackTransforms.run(sessionFolders)
        self.create_2D_pointmatches.run(sessionFolders)
        self.create_HR_tilepairs.run(sessionFolders)
        self.create_HR_pointmatches.run(sessionFolders)
        self.create_fine_aligned_stacks.run(sessionFolders)

        return True

class ConsolidateRoughAlignedStackTransforms(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ConsolidateRoughAlignedStackTransforms")

    def run(self, sessionFolders):
        p = self.paras
        rp = p.renderProject

        for sessionFolder in sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            cmd = "docker exec "+ p.atCoreContainer
            cmd = cmd + " python -m rendermodules.stack.consolidate_transforms"
            cmd = cmd + " --render.host %s"                             %(rp.host)
            cmd = cmd + " --render.project %s"                          %(rp.projectName)
            cmd = cmd + " --render.owner %s"                            %(rp.owner)
            cmd = cmd + " --render.client_scripts %s"                   %(rp.clientScripts)
            cmd = cmd + " --render.memGB %s"                            %(rp.memGB)
            cmd = cmd + " --render.port %s"                             %(rp.hostPort)
            cmd = cmd + " --pool_size %s"                               %(p.atCoreThreads)
            cmd = cmd + " --stack S%d_RoughAligned"                     %(session)
            cmd = cmd + " --output_stack S%d_RoughAligned_Consolidated" %(session)
            cmd = cmd + " --close_stack %d"                             %(True)
            cmd = cmd + " --output_json Test"

            # Run =============
            #self.submit(cmd)


class Create_2D_pointmatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_2D_pointmatches")

    def run(self, sessionFolders):
        p = self.paras
        for sessionFolder in sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)

            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            rp = p.renderProject
            outputFolder  = os.path.join(projectRoot, p.dataOutputFolder)

            match_collection_name = "%s_HR_2D"%(rp.projectName)
            delta = 250

            cmd = "docker exec " + p.sys.atCoreContainer
            cmd = cmd + " python -m renderapps.stitching.create_montage_pointmatches_in_place"
            cmd = cmd + " --render.host %s"                           %(rp.host)
            cmd = cmd + " --render.project %s"                        %(rp.projectName)
            cmd = cmd + " --render.owner %s"                          %(rp.owner)
            cmd = cmd + " --render.client_scripts %s"                 %(rp.clientScripts)
            cmd = cmd + " --render.memGB %s"                          %(rp.memGB)
            cmd = cmd + " --render.port %s"                           %(rp.hostPort)
            cmd = cmd + " --pool_size %s"                             %(p.atCoreThreads)
            cmd = cmd + " --stack S%d_RoughAligned"                   %(session)
            cmd = cmd + " --minZ %d"                                  %(firstSection)
            cmd = cmd + " --maxZ %d"                                  %(lastSection)
            cmd = cmd + " --dataRoot %s"                              %(p.toMount(outputFolder))
            cmd = cmd + " --matchCollection %s"                       %(match_collection_name)
            cmd = cmd + " --delta %d"                                 %(delta)
            cmd = cmd + " --output_json Test"

            # Run =============
            logger.info("Running: " + cmd.replace('--', '\n--'))
            #self.submit(cmd)


class Create_HR_tilepairs(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_HR_tilepairs")

    def run(self, sessionFolders):
        p = self.paras
        rp     = p.renderProject

        for sessionFolder in sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
            input_stack = "S%d_RoughAligned_Consolidated"%(session)

            jsonOutputFolder  = os.path.join(projectRoot, p.dataOutputFolder, "high_res_tilepairfiles")

            # Make sure that the output folder exist
            if os.path.isdir(jsonOutputFolder) == False:
                os.mkdir(jsonOutputFolder)

            jsonfile = os.path.join(jsonOutputFolder, "tilepairs-%d-%d-%d-nostitch.json"     %(p.zNeighborDistance, firstSection, lastSection))

            #Run the TilePairClient
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.0-SNAPSHOT-standalone.jar"
            cmd = cmd + " org.janelia.render.client.TilePairClient"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --owner %s"							    %(rp.owner)
            cmd = cmd + " --project %s"                             %(rp.projectName)
            cmd = cmd + " --stack %s"                               %(input_stack)
            cmd = cmd + " --minZ %d"                                %(firstSection)
            cmd = cmd + " --maxZ %d"                                %(lastSection)
            cmd = cmd + " --toJson %s"                              %(p.toMount(jsonfile))
            cmd = cmd + " --excludeCornerNeighbors %s"              %(p.excludeCornerNeighbors)
            cmd = cmd + " --excludeSameSectionNeighbors %s"         %(p.excludeSameSectionNeighbors)
            cmd = cmd + " --zNeighborDistance %s"                   %(p.zNeighborDistance)
            cmd = cmd + " --xyNeighborFactor %s"                    %(p.xyNeighborFactor)

            #Run =============
            #self.submit(cmd)

            #Prepare json file for the SIFTPointMatch Client
            jsonfileedit      = os.path.join(jsonOutputFolder, "tilepairs-%d-%d-%d-nostitch-EDIT.json"%(p.zNeighborDistance, firstSection, lastSection))
            copyfile(jsonfile, jsonfileedit)
            for line in fileinput.input(jsonfileedit, inplace=True):
                print(line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")


class Create_HR_pointmatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_HR_pointmatches")

    def run(self, sessionFolders):
        p = self.paras
        rp     = p.renderProject

        for sessionFolder in sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            # stacks
            input_stack = "S%d_RoughAligned_Consolidated"%(session)

            #point match collection
            match_collection_name = "%s_HR_3D"%(rp.projectName)

            jsonInputFolder = os.path.join(projectRoot, p.dataOutputFolder, "high_res_tilepairfiles")
            jsonInput       = os.path.join(jsonInputFolder, "tilepairs-%d-%d-%d-nostitch-EDIT.json"     %(p.zNeighborDistance, firstSection, lastSection))

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
            cmd = cmd + " --owner %s"                               %(rp.owner)
            cmd = cmd + " --collection %s"                          %(match_collection_name)
            cmd = cmd + " --pairJson %s"                            %(p.toMount(jsonInput))
            cmd = cmd + " --renderWithFilter true"
            cmd = cmd + " --maxFeatureCacheGb %s"                   %(p.SPARK['maxFeatureCacheGb'])
            #cmd = cmd + " --maxFeatureCacheGb 40"
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




