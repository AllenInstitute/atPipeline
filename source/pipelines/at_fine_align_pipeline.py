import os
import logging
import json
import fileinput
from shutil import copyfile
import at_pipeline as atp
import at_pipeline_process as atpp
from . import at_rough_align_pipeline
import at_utils as u


logger = logging.getLogger('atPipeline')

class FineAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        #self.roughAlignPipeline                     =  at_rough_align_pipeline.RoughAlign(_paras)
        self.consolidateRoughAlignedStackTransforms = ConsolidateRoughAlignedStackTransforms(_paras)
        self.create_2D_pointmatches                 = Create_2D_pointmatches(_paras)
        self.create_HR_tilepairs                    = Create_HR_tilepairs(_paras)
        self.create_HR_pointmatches                 = Create_HR_pointmatches(_paras)
        self.create_fine_aligned_stacks             = Create_fine_aligned_stacks(_paras)

    def run(self):
        atp.ATPipeline.run(self)

        #Run any pre pipeline(s)
        #self.roughAlignPipeline.run()

        self.consolidateRoughAlignedStackTransforms.run()
        logger.newline()

        self.create_2D_pointmatches.run()
        logger.newline()

        self.create_HR_tilepairs.run()
        logger.newline()

        self.create_HR_pointmatches.run()
        logger.newline()

        self.create_fine_aligned_stacks.run()
        logger.newline()

        return True

class ConsolidateRoughAlignedStackTransforms(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ConsolidateRoughAlignedStackTransforms")

##    def validate(self):
##        super().validate()
##        pass

    def run(self):
        super().run()
        p = self.paras
        rp = p.renderProject

        for sessionFolder in self.sessionFolders:
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
            self.submit(cmd)
        self.validate()


class Create_2D_pointmatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_2D_pointmatches")

    def run(self):
        super().run()
        p = self.paras
        for sessionFolder in self.sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)

            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            rp = p.renderProject
            outputFolder  = os.path.join(projectRoot, p.dataOutputFolder)

            match_collection_name = "%s_HR_2D"%(rp.projectName)
            delta = 250

            cmd = "docker exec " + p.atCoreContainer
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
            self.submit(cmd)
        self.validate()

class Create_HR_tilepairs(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_HR_tilepairs")

    def run(self):
        super().run()
        p = self.paras
        rp     = p.renderProject

        for sessionFolder in self.sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
            input_stack = "S%d_RoughAligned_Consolidated"%(session)

            jsonOutputFolder  = os.path.join(projectRoot, p.dataOutputFolder, "high_res_tilepairfiles")

            # Make sure that the output folder exist
            if os.path.isdir(jsonOutputFolder) == False:
                os.mkdir(jsonOutputFolder)

            jsonfile = os.path.join(jsonOutputFolder, "tilepairs-%d-%d-%d-%d-nostitch.json"     %(session, p.zNeighborDistance, firstSection, lastSection))

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
            self.submit(cmd)

            #Prepare json file for the SIFTPointMatch Client
            jsonfileedit      = os.path.join(jsonOutputFolder, "tilepairs-%d-%d-%d-%d-nostitch-EDIT.json"%(session, p.zNeighborDistance, firstSection, lastSection))

            copyfile(jsonfile, jsonfileedit)

            if os.path.isfile(jsonfileedit) == False:
                raise ValueError("The file: " + jsonfileedit + " don't exist. Bailing..")

            for line in fileinput.input(jsonfileedit, inplace=True):
                print(line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")
            self.validate()


class Create_HR_pointmatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_HR_pointmatches")

    def run(self):
        super().run()
        p = self.paras
        rp     = p.renderProject

        for sessionFolder in self.sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            # stacks
            input_stack = "S%d_RoughAligned_Consolidated"%(session)

            #point match collection
            match_collection_name = "%s_HR_3D"%(rp.projectName)

            jsonInputFolder = os.path.join(projectRoot, p.dataOutputFolder, "high_res_tilepairfiles")
            jsonInput       = os.path.join(jsonInputFolder, "tilepairs-%d-%d-%d-%d-nostitch-EDIT.json"     %(session, p.zNeighborDistance, firstSection, lastSection))

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
            self.submit(cmd)

        self.validate()

class Create_fine_aligned_stacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_fine_aligned_stacks")

    def run(self):
        super().run()
        p = self.paras
        rp = p.renderProject

        for sessionFolder in self.sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)

            ribbonLabel = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbonLabel)

            [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

            #Output directories
            dataOutputFolder    = os.path.join(projectRoot, p.dataOutputFolder, "fine_aligned")
            input_json     	    = os.path.join(dataOutputFolder, "input_fine_alignment_%s_%s_%d_%d.json"%(ribbon, session, firstSection, lastSection))
            output_json    	    = os.path.join(dataOutputFolder, "output_fine_alignment_%s_%s_%d_%d.json"%(ribbon, session, firstSection, lastSection))

            #stacks
            input_stack       = "S%d_RoughAligned_Consolidated" %(session)
            output_stack      = "S%d_FineAligned"               %(session)

            rp     = p.renderProject

        	#point match collections
            pm_collection2D     = "%s_HR_2D"%(rp.projectName)
            pm_collection3D     = "%s_HR_3D"%(rp.projectName)

            with open(p.fine_alignment_template) as json_data:
               ra = json.load(json_data)

            #Create folder if not exists
            if os.path.isdir(dataOutputFolder) == False:
                os.mkdir(dataOutputFolder)

            u.saveFineAlignJSON(ra, input_json, rp.host, rp.hostPort, rp.owner, rp.projectName,
                                    input_stack, output_stack, pm_collection2D, pm_collection3D,
                                    rp.clientScripts, rp.logLevel, firstSection, lastSection, p.toMount(dataOutputFolder))

            #Run docker command
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m rendermodules.solver.solve"
            cmd = cmd + " --input_json %s" %(p.toMount(input_json))
            cmd = cmd + " --output_json %s"%(p.toMount(output_json))

            # Run =============
            self.submit(cmd)
        self.validate()

