import os
import logging
import json
import fileinput
from shutil import copyfile
import posixpath
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_stitching_pipeline
from .. import at_utils as u
from .. import at_system_config
from .. import at_spark

logger = logging.getLogger('atPipeline')

class RoughAlign(atp.ATPipeline):

    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.stitchingPipeline     =  at_stitching_pipeline.Stitch(_paras)

        self.append_pipeline_process(CreateLowResStacks(_paras))
        self.append_pipeline_process(CreateLowResTilePairs(_paras))
        self.append_pipeline_process(CreateLowResPointMatches(_paras))
        self.append_pipeline_process(CreateRoughAlignedStacks(_paras))
        self.append_pipeline_process(ApplyLowResToHighRes(_paras))

    def run(self):
        #Run any pre pipeline(s)
        self.stitchingPipeline.run()

        atp.ATPipeline.run(self)
        return True

#-----------------------------------------------------------------------------------------------

class CreateLowResStacks(atpp.PipelineProcess):

    def __init__(self, _paras : at_system_config.ATSystemConfig):
        super().__init__(_paras, "CreateLowResStacks")

    #def check_if_done(self):
    #    pass

    def validate(self):
        #Just write 'True' to the status file
        with open(self.status_file,'w') as f:
            f.truncate()
            f.write('True')
        return True

    def run(self):
        super().run()
        p = self.paras

        for session in p.sessions:
            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))

            firstRibbon = int (p.ribbons[0][6:])
            lastRibbon = int(p.ribbons[-1][6:])

            # output directories
            downsample_dir   = os.path.join(p.absoluteDataOutputFolder, "low_res")
            numsections_file = os.path.join(downsample_dir,             "numsections-%s"%(sessionNR))

            # Make sure output folder exist
            if os.path.isdir(downsample_dir) == False:
                os.mkdir(downsample_dir)

            # stacks
            input_stack  = "S%d_Stitched_Dropped"   %(sessionNR)
            output_stack = "S%d_LowRes" %(sessionNR)

            rp = p.renderProject

            # docker commands
            cmd =       "/opt/conda/bin/python -m renderapps.materialize.make_downsample_image_stack"
            cmd = cmd + " --render.host %s"                                %(rp.host)
            cmd = cmd + " --render.project %s"                             %(rp.project_name)
            cmd = cmd + " --render.owner %s"                               %(rp.owner)
            cmd = cmd + " --render.client_scripts %s"                      %(rp.clientScripts)
            cmd = cmd + " --render.memGB %s"                               %(rp.memGB)
            cmd = cmd + " --render.port %s"                                %(rp.hostPort)
            cmd = cmd + " --log_level %s"                                  %(rp.logLevel)
            cmd = cmd + " --input_stack %s"                                %(input_stack)
            cmd = cmd + " --output_stack %s"                               %(output_stack)
            cmd = cmd + " --image_directory %s"                            %(p.toMount(downsample_dir))
            cmd = cmd + " --pool_size %s"                                  %(p.GENERAL['AT_CORE_THREADS'])
            cmd = cmd + " --scale %s"                                      %(p.CREATE_LOWRES_STACKS['SCALE'])
            cmd = cmd + " --minZ %s"                                       %(firstRibbon*100)
            cmd = cmd + " --maxZ %s"                                       %((lastRibbon + 1)*100 - 1)
            cmd = cmd + " --numsectionsfile %s"                            %(p.toMount(numsections_file))

            # Run =============
            self.submit_atcore(cmd)


#Note, this seem to require at least two sections to work which makes sense, so tell the user that
class CreateLowResTilePairs(atpp.PipelineProcess):

    def __init__(self, _paras : at_system_config.ATSystemConfig):
        super().__init__(_paras, "CreateLowResTilePairs")

    #def check_if_done(self):
    #    pass

    def run(self):
        super().run()
        p = self.paras

        for session in p.sessions:
            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))

            inputStack  = "S%d_LowRes"%(sessionNR)
            rp          = p.renderProject
            jsondir     = os.path.join(p.absoluteDataOutputFolder, "lowres_tilepairfiles")

            # Make sure output folder exist
            if os.path.isdir(jsondir) == False:
                os.mkdir(jsondir)

            jsonfile = os.path.join(jsondir, "tilepairs-%d-%s-%d-%d-nostitch.json"     %(sessionNR, p.LOWRES_TILE_PAIR_CLIENT['Z_NEIGHBOR_DISTANCE'], p.firstSection, p.lastSection))

            #Run the TilePairClient
            cmd =       "java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.0-SNAPSHOT-standalone.jar"
            cmd = cmd + " org.janelia.render.client.TilePairClient"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --owner %s"							    %(rp.owner)
            cmd = cmd + " --project %s"                             %(rp.project_name)
            cmd = cmd + " --stack %s"                               %(inputStack)
            cmd = cmd + " --minZ %d"                                %(p.firstSection)
            cmd = cmd + " --maxZ %d"                                %(p.lastSection)
            cmd = cmd + " --toJson %s"                              %(p.toMount(jsonfile))
            cmd = cmd + " --excludeCornerNeighbors %s"              %(u.toBool(p.LOWRES_TILE_PAIR_CLIENT['EXCLUDE_CORNER_NEIGHBOURS']))
            cmd = cmd + " --excludeSameSectionNeighbors %s"         %(u.toBool(p.LOWRES_TILE_PAIR_CLIENT['EXCLUDE_SAME_SECTION_NEIGHBOR']))
            cmd = cmd + " --zNeighborDistance %s"                   %(p.LOWRES_TILE_PAIR_CLIENT['Z_NEIGHBOR_DISTANCE'])
            cmd = cmd + " --xyNeighborFactor %s"                    %(p.LOWRES_TILE_PAIR_CLIENT['XY_NEIGHBOR_FACTOR'])

            #Run =============
            self.submit_atcore(cmd)

            #Prepare json file for the SIFTPointMatch Client
            jsonfileedit      = os.path.join(jsondir, "tilepairs-%d-%s-%d-%d-nostitch-EDIT.json"%(sessionNR, p.LOWRES_TILE_PAIR_CLIENT['Z_NEIGHBOR_DISTANCE'], p.firstSection, p.lastSection))
            copyfile(jsonfile, jsonfileedit)

            for line in fileinput.input(jsonfileedit, inplace=True):
                print(line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")


class CreateLowResPointMatches(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateLowResPointMatches")

    #def check_if_done(self):
    #    pass

    def run(self):
        super().run()
        p = self.paras

        for session in p.sessions:
            sessionNR = int(session[7:])

            logger.info("Processing session: " + str(sessionNR))

            #Optimize spark parameters
            data_info = []


            spark = at_spark.Spark(int(p.config['GENERAL']['HOST_MEMORY']), int(p.config['GENERAL']['HOST_NUMBER_OF_CORES']), data_info)

            #output directories
            downsample_dir   = os.path.join(p.absoluteDataOutputFolder, "low_res")

            jsondir  = os.path.join(p.absoluteDataOutputFolder, "lowres_tilepairfiles")
            jsonfile = os.path.join(jsondir, "tilepairs-%d-%s-%d-%d-nostitch-EDIT.json"     %(sessionNR, p.LOWRES_TILE_PAIR_CLIENT['Z_NEIGHBOR_DISTANCE'], p.firstSection, p.lastSection))

            rp     = p.renderProject

            #SIFT Point Match Client
            cmd =       "/usr/spark-2.0.2/bin/spark-submit"
            cmd = cmd + " --conf spark.default.parallelism=%s"      %(spark.default_parallelism)
            cmd = cmd + " --driver-memory %s"                       %(str(spark.driver_memory) + "g")
            cmd = cmd + " --executor-memory %s"                     %(str(spark.executor_memory) + "g")
            cmd = cmd + " --executor-cores %s"                      %(str(spark.executor_cores) )
            cmd = cmd + " --class org.janelia.render.client.spark.SIFTPointMatchClient"
            cmd = cmd + " --name PointMatchFull"
            cmd = cmd + " --master local[%s] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.1.0-SNAPSHOT-standalone.jar"%(p.config['GENERAL']['SPARK_WORKER_THREADS'])
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --collection %s_lowres_round"             %(rp.project_name)
            cmd = cmd + " --owner %s"                               %(rp.owner)
            cmd = cmd + " --pairJson %s"                            %(p.toMount(jsonfile))
            cmd = cmd + " --renderWithFilter %s"                    %(p.LOWRES_POINTMATCHES['RENDER_WITH_FILTER'])
            cmd = cmd + " --maxFeatureCacheGb %s"                   %(p.LOWRES_POINTMATCHES['MAX_FEATURE_CACHE_GB'])
            cmd = cmd + " --matchModelType %s"                      %(p.LOWRES_POINTMATCHES['MATCH_MODEL_TYPE'])
            cmd = cmd + " --matchMinNumInliers %s"                  %(p.LOWRES_POINTMATCHES['MATCH_MIN_NUMBER_OF_INLIERS'])
            #cmd = cmd + " --matchMaxEpsilon %s"                     %(p.LOWRES_POINTMATCHES['MATCH_MAX_EPSILON'])
            #cmd = cmd + " --matchMaxTrust %s"                       %(p.LOWRES_POINTMATCHES['MATCH_AX_TRUST'])

            cmd = cmd + " --SIFTmaxScale %s"                        %(p.LOWRES_POINTMATCHES['SIFT_MAX_SCALE'])
            cmd = cmd + " --SIFTminScale %s"                        %(p.LOWRES_POINTMATCHES['SIFT_MIN_SCALE'])
            cmd = cmd + " --SIFTsteps %s"                           %(p.LOWRES_POINTMATCHES['SIFT_STEPS'])
            cmd = cmd + " --renderScale %s"                         %(p.LOWRES_POINTMATCHES['RENDER_SCALE'])
            cmd = cmd + " --matchRod %s"                            %(p.LOWRES_POINTMATCHES['MATCH_ROD'])
            #cmd = cmd + " --matchFilter %s"                         %(p.LOWRES_POINTMATCHES['CONSENSUS_SETS'])

            #Run =============
            self.submit_atcore(cmd)


class CreateRoughAlignedStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateRoughAlignedStacks")

    #def check_if_done(self):
    #    pass
    def saveRoughAlignJSON(self, template, outFile, renderProject, input_stack, output_stack, lowresPmCollection, nFirst, nLast, dataOutputFolder):
        template['regularization']['log_level']                  = renderProject.logLevel
        template['matrix_assembly']['log_level']                 = renderProject.logLevel

        template['output_stack']['client_scripts']               = renderProject.clientScripts
        template['output_stack']['owner']                        = renderProject.owner
        template['output_stack']['log_level']                    = renderProject.logLevel
        template['output_stack']['project']                      = renderProject.project_name
        template['output_stack']['port']                         = renderProject.hostPort
        template['output_stack']['host']                         = renderProject.host
        template['output_stack']['name']                         = output_stack

        template['input_stack']['client_scripts']                = renderProject.clientScripts
        template['input_stack']['owner']                         = renderProject.owner
        template['input_stack']['log_level']                     = renderProject.logLevel
        template['input_stack']['project']                       = renderProject.project_name
        template['input_stack']['port']                          = renderProject.hostPort
        template['input_stack']['host']                          = renderProject.host
        template['input_stack']['name']                          = input_stack

        template['pointmatch']['client_scripts']                 = renderProject.clientScripts
        template['pointmatch']['owner']                          = renderProject.owner
        template['pointmatch']['log_level']                      = renderProject.logLevel
        template['pointmatch']['project']                        = renderProject.project_name
        template['pointmatch']['name']                           = lowresPmCollection
        template['pointmatch']['port']                           = renderProject.hostPort
        template['pointmatch']['host']                           = renderProject.host

        template['hdf5_options']['log_level']                    = renderProject.logLevel
        template['hdf5_options']['output_dir']                   = dataOutputFolder

        template['first_section']                                = nFirst
        template['last_section']                                 = nLast
        template['log_level']                                    = "INFO"
        u.dump_json(template, outFile)

    def run(self):
        super().run()
        p = self.paras
        rp  = p.renderProject

        for session in p.sessions:
            sessionNR = int(session[7:])
            logger.info("Processing session: " + str(sessionNR))

            #Output directories
            dataOutputFolder    = os.path.join(p.absoluteDataOutputFolder, "rough_aligned")
            input_json          = os.path.join(dataOutputFolder, "roughalignment_%s_%d_%d.json"       %(sessionNR, p.firstSection, p.lastSection))
            output_json         = os.path.join(dataOutputFolder, "output_roughalignment_%s_%d_%d.json"%(sessionNR, p.firstSection, p.lastSection))

            #stacks
            inputStack     = "S%d_LowRes"%(sessionNR)
            outputStack    = "S%d_RoughAligned_LowRes"%(sessionNR)

        	#point match collections
            lowresPmCollection = "%s_lowres_round"%rp.project_name

            #Check for Pointmatch collection.. if not found bail...

            with open(p.alignment_template) as json_data:
               ra = json.load(json_data)

            #Create folder if not exists
            if os.path.isdir(dataOutputFolder) == False:
                os.mkdir(dataOutputFolder)

            self.saveRoughAlignJSON(ra, input_json, rp, inputStack, outputStack, lowresPmCollection, p.firstSection, p.lastSection, p.toMount(dataOutputFolder))

            #Run docker command
            cmd =       "/opt/conda/bin/python -m rendermodules.solver.solve"
            cmd = cmd + " --input_json %s" %(p.toMount(input_json))
            cmd = cmd + " --output_json %s"%(p.toMount(output_json))
            self.submit_atcore(cmd)

class ApplyLowResToHighRes(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "ApplyLowResToHighRes")

##    def check_if_done(self):
##        pass

    def run(self):
        super().run()
        p = self.paras

        for session in p.sessions:
            sessionNR = int(session[7:])

            logger.info("Processing session: " + str(sessionNR))

            lowresStack             = "S%d_RoughAligned_LowRes"%(sessionNR)

            inputStack              = "S%d_Stitched_Dropped"%(sessionNR)
            outputStack             = "S%d_RoughAligned"%(sessionNR)

            rp                      = p.renderProject

            roughalign_ts_dir = os.path.join(p.absoluteDataOutputFolder, "rough_aligned_tilespecs")

            # Make sure output folder exist
            if os.path.isdir(roughalign_ts_dir) == False:
                os.mkdir(roughalign_ts_dir)

            #Run docker command
            cmd =       "/opt/conda/bin/python -m renderapps.rough_align.ApplyLowRes2HighRes"
            cmd = cmd + " --render.host %s"                %(rp.host)
            cmd = cmd + " --render.owner %s "              %(rp.owner)
            cmd = cmd + " --render.project %s"             %(rp.project_name)
            cmd = cmd + " --render.client_scripts %s"      %(rp.clientScripts)
            cmd = cmd + " --render.port %d"                %(rp.hostPort)
            cmd = cmd + " --render.memGB %s"               %(rp.memGB)
            cmd = cmd + " --pool_size %s"                  %(p.GENERAL['AT_CORE_THREADS'])
            cmd = cmd + " --tilespec_directory %s"         %(p.toMount(roughalign_ts_dir))
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
