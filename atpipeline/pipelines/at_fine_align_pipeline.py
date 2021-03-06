import os
import logging
import json
import fileinput
from shutil import copyfile
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_rough_align_pipeline
from .. import at_utils as u
from .. import at_spark


logger = logging.getLogger('atPipeline')

class FineAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)
        self.name = "finealign"
        #Define the pipeline
        self.roughAlignPipeline = at_rough_align_pipeline.RoughAlign(_paras)

        self.append_pipeline_process(ConsolidateRoughAlignedStackTransforms(_paras))
        self.append_pipeline_process(Create_2D_pointmatches(_paras))
        self.append_pipeline_process(Create_HR_tilepairs(_paras))
        self.append_pipeline_process(Create_HR_pointmatches(_paras))
        self.append_pipeline_process(Create_fine_aligned_stacks(_paras))

    def run(self):
        #Run any pre pipeline(s)
        self.roughAlignPipeline.run()
        atp.ATPipeline.run(self)
        return True

class ConsolidateRoughAlignedStackTransforms(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ConsolidateRoughAlignedStackTransforms")

    def run(self):
        super().run()
        p = self.paras
        rp = p.renderProject

        jsonOutputFolder  = os.path.join(p.absoluteDataOutputFolder, "consolidated_transforms")

        # Make sure that the output folder exist
        if os.path.isdir(jsonOutputFolder) == False:
            os.mkdir(jsonOutputFolder)

        for session in p.sessions:
            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))

            cmd =       "/opt/conda/bin/python -m rendermodules.stack.consolidate_transforms"
            cmd = cmd + " --render.host %s"                             %(rp.host)
            cmd = cmd + " --render.project %s"                          %(rp.project_name)
            cmd = cmd + " --render.owner %s"                            %(rp.owner)
            cmd = cmd + " --render.client_scripts %s"                   %(rp.clientScripts)
            cmd = cmd + " --render.memGB %s"                            %(rp.memGB)
            cmd = cmd + " --render.port %s"                             %(rp.hostPort)
            cmd = cmd + " --pool_size %s"                               %(p.GENERAL['AT_CORE_THREADS'])
            cmd = cmd + " --stack S%d_RoughAligned"                     %(sessionNR)
            cmd = cmd + " --output_stack S%d_RoughAligned_Consolidated" %(sessionNR)
            cmd = cmd + " --close_stack %d"                             %(True)
            cmd = cmd + " --output_json %s"%(p.toMount(os.path.join(jsonOutputFolder, "out.json")))

            # Run =============
            self.submit_atcore(cmd)

class Create_2D_pointmatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_2D_pointmatches")

    def run(self):
        super().run()

        p = self.paras

        jsonOutputFolder  = os.path.join(p.absoluteDataOutputFolder, "consolidated_transforms")

        # Make sure that the output folder exist
        if os.path.isdir(jsonOutputFolder) == False:
            os.mkdir(jsonOutputFolder)

        for session in p.sessions:
            #Check which ribbon we are processing, and adjust section numbers accordingly
            current_ribbon = u.getRibbonLabelFromSessionFolder(self.sessionFolders[0])
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)
            nr_of_tiles_in_section = u.get_number_of_physical_tiles_in_section(firstSection, current_ribbon, p.dataInfo)
            if nr_of_tiles_in_section <= 1:
                break

            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))

            rp = p.renderProject

            cmd =       "/opt/conda/bin/python -m renderapps.stitching.create_montage_pointmatches_in_place"
            cmd = cmd + " --render.host %s"                           %(rp.host)
            cmd = cmd + " --render.project %s"                        %(rp.project_name)
            cmd = cmd + " --render.owner %s"                          %(rp.owner)
            cmd = cmd + " --render.client_scripts %s"                 %(rp.clientScripts)
            cmd = cmd + " --render.memGB %s"                          %(rp.memGB)
            cmd = cmd + " --render.port %s"                           %(rp.hostPort)
            cmd = cmd + " --pool_size %s"                             %(p.GENERAL['AT_CORE_THREADS'])
            cmd = cmd + " --stack S%d_RoughAligned"                   %(sessionNR)
            cmd = cmd + " --minZ %d"                                  %(p.firstSection)
            cmd = cmd + " --maxZ %d"                                  %(p.lastSection)
            cmd = cmd + " --dataRoot %s"                              %(p.toMount(p.absoluteDataOutputFolder))
            cmd = cmd + " --matchCollection %s"                       %("%s_HR_2D"%(rp.project_name))
            cmd = cmd + " --delta %s"                                 %(p.CREATE_2D_POINTMATCHES['DELTA'])
            cmd = cmd + " --output_json %s"%(p.toMount(os.path.join(jsonOutputFolder, "out2.json")))

            # Run =============
            self.submit_atcore(cmd)


class Create_HR_tilepairs(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_HR_tilepairs")

    def run(self):
        super().run()
        p = self.paras
        rp     = p.renderProject

        for session in p.sessions:
            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))

            jsonOutputFolder  = os.path.join(p.absoluteDataOutputFolder, "high_res_tilepairfiles")

            # Make sure that the output folder exist
            if os.path.isdir(jsonOutputFolder) == False:
                os.mkdir(jsonOutputFolder)

            jsonfile = os.path.join(jsonOutputFolder, "tilepairs-%s-%s-%s-%s-nostitch.json"     %(sessionNR, p.CREATE_HR_TILEPAIRS['Z_NEIGHBOR_DISTANCE'], p.firstSection, p.lastSection))

            #Run the TilePairClient
            cmd =       "java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.1-SNAPSHOT-standalone.jar"
            cmd = cmd + " org.janelia.render.client.TilePairClient"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --owner %s"							    %(rp.owner)
            cmd = cmd + " --project %s"                             %(rp.project_name)
            cmd = cmd + " --stack %s"                               %("S%d_RoughAligned_Consolidated"%(sessionNR))
            cmd = cmd + " --minZ %d"                                %(p.firstSection)
            cmd = cmd + " --maxZ %d"                                %(p.lastSection)
            cmd = cmd + " --toJson %s"                              %(p.toMount(jsonfile))
            cmd = cmd + " --excludeCornerNeighbors %s"              %(u.toBool(p.CREATE_HR_TILEPAIRS['EXCLUDE_CORNER_NEIGHBORS']))
            cmd = cmd + " --excludeSameSectionNeighbors %s"         %(u.toBool(p.CREATE_HR_TILEPAIRS['EXCLUDE_SAME_SECTION_NEIGHBORS']))
            cmd = cmd + " --zNeighborDistance %s"                   %(p.CREATE_HR_TILEPAIRS['Z_NEIGHBOR_DISTANCE'])
            cmd = cmd + " --xyNeighborFactor %s"                    %(p.CREATE_HR_TILEPAIRS['XY_NEIGHBOR_FACTOR'])

            #Run =============
            self.submit_atcore(cmd)

            #Prepare json file for the SIFTPointMatch Client
            jsonfileedit      = os.path.join(jsonOutputFolder, "tilepairs-%s-%s-%d-%d-nostitch-EDIT.json"%(sessionNR, p.CREATE_HR_TILEPAIRS['Z_NEIGHBOR_DISTANCE'], p.firstSection, p.lastSection))

            copyfile(jsonfile, jsonfileedit)

            if os.path.isfile(jsonfileedit) == False:
                raise ValueError("The file: " + jsonfileedit + " don't exist. Bailing..")

            for line in fileinput.input(jsonfileedit, inplace=True):
                print(line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")


class Create_HR_pointmatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_HR_pointmatches")

    def run(self):
        super().run()
        p = self.paras
        rp     = p.renderProject

        for session in p.sessions:
            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))


            jsonInputFolder = os.path.join(p.absoluteDataOutputFolder, "high_res_tilepairfiles")
            jsonInput       = os.path.join(jsonInputFolder, "tilepairs-%s-%s-%d-%d-nostitch-EDIT.json"     %(sessionNR, p.CREATE_HR_TILEPAIRS['Z_NEIGHBOR_DISTANCE'], p.firstSection, p.lastSection))

            data_info = []
            spark = at_spark.Spark(int(p.config['GENERAL']['HOST_MEMORY']), int(p.config['GENERAL']['HOST_NUMBER_OF_CORES']), data_info)

            #SIFT Point Match Client
            cmd =       "/pipeline/spark_wrapper.sh /usr/spark-2.0.2/bin/spark-submit"
            cmd = cmd + " --conf spark.default.parallelism=%s"      %(spark.default_parallelism)
            cmd = cmd + " --driver-memory %s"                       %(str(spark.driver_memory) + "g")
            cmd = cmd + " --executor-memory %s"                     %(str(spark.executor_memory) + "g")
            cmd = cmd + " --executor-cores %s"                      %(str(spark.executor_cores) )
            cmd = cmd + " --class org.janelia.render.client.spark.SIFTPointMatchClient"
            cmd = cmd + " --name PointMatchFull"
            cmd = cmd + " --master local[%s] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.1.1-SNAPSHOT-standalone.jar"%(p.config['GENERAL']['SPARK_WORKER_THREADS'])
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --owner %s"                               %(rp.owner)
            cmd = cmd + " --collection %s"                          %("%s_HR_3D"%(rp.project_name))
            cmd = cmd + " --pairJson %s"                            %(p.toMount(jsonInput))
            cmd = cmd + " --renderWithFilter true"
            cmd = cmd + " --maxFeatureCacheGb %s"                   %(p.CREATE_HR_POINTMATCHES['MAX_FEATURE_CACHE_GB'])
            cmd = cmd + " --matchModelType %s"                      %(p.CREATE_HR_POINTMATCHES['MATCH_MODEL_TYPE'])
            cmd = cmd + " --matchMinNumInliers %s"                  %(p.CREATE_HR_POINTMATCHES['MATCH_MIN_NUMBER_OF_INLIERS'])
            #cmd = cmd + " --matchMaxEpsilon 15.0"
            #cmd = cmd + " --matchMaxTrust 1.0"

            cmd = cmd + " --SIFTmaxScale %s"                        %(p.CREATE_HR_POINTMATCHES['SIFT_MAX_SCALE'])
            cmd = cmd + " --SIFTminScale %s"                        %(p.CREATE_HR_POINTMATCHES['SIFT_MIN_SCALE'])
            cmd = cmd + " --SIFTsteps %s"                           %(p.CREATE_HR_POINTMATCHES['SIFT_STEPS'])
            cmd = cmd + " --renderScale %s"                         %(p.CREATE_HR_POINTMATCHES['RENDER_SCALE'])
            cmd = cmd + " --matchRod %s"                            %(p.CREATE_HR_POINTMATCHES['MATCH_ROD'])
            #cmd = cmd + " --matchFilter CONSENSUS_SETS"
            self.submit_atcore(cmd)

class Create_fine_aligned_stacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "Create_fine_aligned_stacks")

    def saveFineAlignJSON(self, template, outFile, renderHost, port, owner, project, input_stack, output_stack, collection_2D, collection_3D, clientScripts, logLevel, nFirst, nLast, dataOutputFolder):
        template['regularization']['log_level']                  = logLevel
        template['matrix_assembly']['log_level']                 = logLevel

        template['output_stack']['client_scripts']               = clientScripts
        template['output_stack']['owner']                        = owner
        template['output_stack']['log_level']                    = logLevel
        template['output_stack']['project']                      = project
        template['output_stack']['name']                         = output_stack
        template['output_stack']['port']                         = port
        template['output_stack']['host']                         = renderHost

        template['input_stack']['client_scripts']                = clientScripts
        template['input_stack']['owner']                         = owner
        template['input_stack']['log_level']                     = logLevel
        template['input_stack']['project']                       = project
        template['input_stack']['port']                          = port
        template['input_stack']['host']                          = renderHost
        template['input_stack']['name']                          = input_stack

        template['pointmatch']['client_scripts']                 = clientScripts
        template['pointmatch']['owner']                          = owner
        template['pointmatch']['log_level']                      = logLevel
        template['pointmatch']['project']                        = project

        if collection_2D != None:
            template['pointmatch']['name']                           = [collection_2D, collection_3D]
        else:
            template['pointmatch']['name']                           = [collection_3D]

        template['pointmatch']['port']                           = port
        template['pointmatch']['host']                           = renderHost

        template['hdf5_options']['log_level']                    = logLevel
        template['hdf5_options']['output_dir']                   = dataOutputFolder

        template['last_section']                                 = nLast
        template['first_section']                                = nFirst
        template['log_level']                                    = "INFO"
        u.dump_json(template, outFile)


    def run(self):
        super().run()
        p = self.paras
        rp = p.renderProject

        for session in p.sessions:
            sessionNR = int(session[7:])

            logger.info("Processing session: " + str(sessionNR))

            #Output directories
            dataOutputFolder    = os.path.join(p.absoluteDataOutputFolder, "fine_aligned")

            #Create folder if not exists
            if os.path.isdir(dataOutputFolder) == False:
                os.mkdir(dataOutputFolder)

            input_json     	    = os.path.join(dataOutputFolder, "input_fine_alignment_%s_%d_%d.json"%(sessionNR,  p.firstSection, p.lastSection))
            output_json    	    = os.path.join(dataOutputFolder, "output_fine_alignment_%s_%d_%d.json"%(sessionNR, p.firstSection, p.lastSection))

            #stacks
            input_stack       = "S%d_RoughAligned_Consolidated" %(sessionNR)
            output_stack      = "S%d_FineAligned"               %(sessionNR)

            rp     = p.renderProject

        	#point match collections
            pm_collection2D     = "%s_HR_2D"%(rp.project_name)
            pm_collection3D     = "%s_HR_3D"%(rp.project_name)

            with open(p.fine_alignment_template) as json_data:
               ra = json.load(json_data)

            #Testing__single_tile_HR_2D
            current_ribbon = u.getRibbonLabelFromSessionFolder(self.sessionFolders[0])
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)
            nr_of_tiles_in_section = u.get_number_of_physical_tiles_in_section(firstSection, current_ribbon, p.dataInfo)
            if nr_of_tiles_in_section <= 1:
                pm_collection2D = None

            self.saveFineAlignJSON(ra, input_json, rp.host, rp.hostPort, rp.owner, rp.project_name,
                                    input_stack, output_stack, pm_collection2D, pm_collection3D,
                                    rp.clientScripts, rp.logLevel, p.firstSection, p.lastSection, p.toMount(dataOutputFolder))

            #Run docker command
            cmd =       "/opt/conda/bin/python -m rendermodules.solver.solve"
            cmd = cmd + " --input_json %s" %(p.toMount(input_json))
            cmd = cmd + " --output_json %s"%(p.toMount(output_json))

            # Run =============
            self.submit_atcore(cmd)
