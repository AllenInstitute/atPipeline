import os
import logging
import json
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from . import at_stitching_pipeline
from .. import at_utils as u
from .. import at_system_config
import fileinput
from shutil import copyfile
import posixpath

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
        atp.ATPipeline.run(self)

        #Run any pre pipeline(s)
        self.stitchingPipeline.run()

        #Iterate through the pipeline
        for process in self.pipeline_processes:

            if process.check_if_done() == False:
                process.run()

                #Validate the result of the run
                res = process.validate()

                if res == False:
                    logger.info("Failed in pipelinestep" + process.get_name())
                    return False
            else:
                logger.info("Skipping pipeline step: " + process.get_name())


        return True


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
        try:
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
                cmd = "docker exec " + p.atCoreContainer
                cmd = cmd + " /opt/conda/bin/python -m renderapps.materialize.make_downsample_image_stack"
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
                return True
        except:
            return False


#Note, this seem to require at least two sections to work which makes sense, so tell the user that
class CreateLowResTilePairs(atpp.PipelineProcess):

    def __init__(self, _paras : at_system_config.ATSystemConfig):
        super().__init__(_paras, "CreateLowResTilePairs")

    #def check_if_done(self):
    #    pass

    def run(self):
        super().run()
        p = self.paras

        firstRibbon = int (p.ribbons[0][6:])
        lastRibbon = int(p.ribbons[-1][6:])


        for session in p.sessions:
            sessionNR = int(session[7:])

            logger.info("Processing session: " + str(sessionNR))

            inputStack = "S%d_LowRes"%(sessionNR)

            rp      = p.renderProject
            jsondir = os.path.join(p.absoluteDataOutputFolder, "lowres_tilepairfiles")

            # Make sure output folder exist
            if os.path.isdir(jsondir) == False:
                os.mkdir(jsondir)

            jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-%d-nostitch.json"     %(sessionNR, p.zNeighborDistance, p.firstSection, p.lastSection))

            #Run the TilePairClient
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.0-SNAPSHOT-standalone.jar"
            cmd = cmd + " org.janelia.render.client.TilePairClient"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --owner %s"							    %(rp.owner)
            cmd = cmd + " --project %s"                             %(rp.projectName)
            cmd = cmd + " --stack %s"                               %(inputStack)
            cmd = cmd + " --minZ %d"                                %(p.firstSection)
            cmd = cmd + " --maxZ %d"                                %(p.lastSection)
            cmd = cmd + " --toJson %s"                              %(p.toMount(jsonfile))
            cmd = cmd + " --excludeCornerNeighbors %s"              %(p.excludeCornerNeighbors)
            cmd = cmd + " --excludeSameSectionNeighbors %s"         %(p.excludeSameSectionNeighbors)
            cmd = cmd + " --zNeighborDistance %s"                   %(p.zNeighborDistance)
            cmd = cmd + " --xyNeighborFactor %s"                    %(p.xyNeighborFactor)

            #Run =============
            self.submit(cmd)

            #Prepare json file for the SIFTPointMatch Client
            jsonfileedit      = os.path.join(jsondir, "tilepairs-%d-%d-%d-%d-nostitch-EDIT.json"%(sessionNR, p.zNeighborDistance, p.firstSection, p.lastSection))
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

            rp     = p.renderProject

            #output directories
            downsample_dir   = os.path.join(p.absoluteDataOutputFolder, "low_res")

            jsondir  = os.path.join(p.absoluteDataOutputFolder, "lowres_tilepairfiles")
            jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-%d-nostitch-EDIT.json"     %(sessionNR, p.zNeighborDistance, p.firstSection, p.lastSection))

            #SIFT Point Match Client
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " /usr/spark-2.0.2/bin/spark-submit"

            cmd = cmd + " --conf spark.default.parallelism=%s"      %(p.LOWRES_POINTMATCHES['SPARK_DEFAULT_PARALLELISM'])
            cmd = cmd + " --driver-memory %s"                       %(p.LOWRES_POINTMATCHES['SPARK_DRIVER_MEMORY'])
            cmd = cmd + " --executor-memory %s"                     %(p.LOWRES_POINTMATCHES['SPARK_EXECUTOR_MEMORY'])
            cmd = cmd + " --executor-cores %s"                      %(p.LOWRES_POINTMATCHES['SPARK_EXECUTOR_CORES'])

            cmd = cmd + " --class org.janelia.render.client.spark.SIFTPointMatchClient"
            cmd = cmd + " --name PointMatchFull"
            cmd = cmd + " --master local[*] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.1.0-SNAPSHOT-standalone.jar"
            cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
            cmd = cmd + " --collection %s_lowres_round"             %(rp.projectName)
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
            self.submit(cmd)


class CreateRoughAlignedStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateRoughAlignedStacks")

    #def check_if_done(self):
    #    pass

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
            lowresPmCollection = "%s_lowres_round"%rp.projectName

            with open(p.alignment_template) as json_data:
               ra = json.load(json_data)

            #Create folder if not exists
            if os.path.isdir(dataOutputFolder) == False:
                os.mkdir(dataOutputFolder)

            u.saveRoughAlignJSON(ra, input_json, rp, inputStack, outputStack, lowresPmCollection, p.firstSection, p.lastSection, p.toMount(dataOutputFolder))

            #Run docker command
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " /opt/conda/bin/python -m rendermodules.solver.solve"
            cmd = cmd + " --input_json %s" %(p.toMount(input_json))
            cmd = cmd + " --output_json %s"%(p.toMount(output_json))
            self.submit(cmd)

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

            lowresStack             = "S%d_LowRes"%(sessionNR)

            inputStack              = "S%d_Stitched_Dropped"%(sessionNR)
            outputStack             = "S%d_RoughAligned"%(sessionNR)

            rp                      = p.renderProject

            roughalign_ts_dir = os.path.join(p.absoluteDataOutputFolder, "rough_aligned_tilespecs")

            # Make sure output folder exist
            if os.path.isdir(roughalign_ts_dir) == False:
                os.mkdir(roughalign_ts_dir)

            #Run docker command
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " /opt/conda/bin/python -m renderapps.rough_align.ApplyLowRes2HighRes"
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

            #cmd = cmd + " --minZ 0"#%d"                  %(p.firstSection*100)
            #cmd = cmd + " --maxZ 5000"#%d"                  %(p.lastSection*100)
            first_ribbon = int(p.ribbons[0][6:])
            last_ribbon  = int(p.ribbons[-1][6:])

            cmd = cmd + " --minZ %d --maxZ %d"       %(first_ribbon*100, (last_ribbon+1) * 100)

            self.submit(cmd)
