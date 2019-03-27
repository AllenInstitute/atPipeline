import os
import logging
import json
import at_pipeline as atp
import at_pipeline_process as atpp
import at_utils as u
import posixpath

logger = logging.getLogger('atPipeline')

class Stitch(atp.ATPipeline):
    def __init__(self, _paras):
        super().__init__(_paras)

        p = self.parameters

        #Define the pipeline
        self.create_state_tables              = CreateStateTables(p)
        self.create_raw_data_render_stacks    = CreateRawDataRenderStacks(p)
        self.create_median_files              = CreateMedianFiles(p)
        self.create_flatfield_corrected_data  = CreateFlatFieldCorrectedData(p)
        self.create_stitched_sections         = CreateStitchedSections(p)
        self.drop_stitching_mistakes          = DropStitchingMistakes(p)



    def run(self):
        atp.ATPipeline.run(self)
        #Check what pipeline to run
        for ribbon in self.parameters.ribbons:
            sessionFolders = []
            #Create session folders
            for session in self.parameters.sessions:
              sessionFolders.append(os.path.join(self.parameters.projectDataFolder, self.parameters.projectDataFolder, "raw", "data", ribbon, session))

            for sessionFolder in sessionFolders:
                self.create_state_tables.run(sessionFolder)
                self.create_raw_data_render_stacks.run(sessionFolder)
                self.create_median_files.run(sessionFolder)
                self.create_flatfield_corrected_data.run(sessionFolder)
                self.create_stitched_sections.run(sessionFolder)
                self.drop_stitching_mistakes.run(sessionFolder)

        return True


##Sub processes in the stitching pipeline are defined below

class CreateStateTables(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateStateTables")

    def run(self, sessionFolder):
        atpp.PipelineProcess.run(self, sessionFolder)
        logger.info("=========== Creating state tables for session: " + sessionFolder + " ===============")

        for sectnum in range(self.paras.firstSection, self.paras.lastSection + 1):
            logger.debug("Processing section: " + str(sectnum))

            #State table file
            statetablefile = self.paras.getStateTableFileName(self.ribbon, self.session, sectnum)
            logger.info("Creating statetable file: " + statetablefile)

            if os.path.exists(statetablefile) and self.paras.overwritedata == False:
               logger.info("The statetable: " + statetablefile + " already exists. Continuing..")
            else:
                cmd = "docker exec " + self.paras.atCoreContainer
                cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
                cmd = cmd + " --projectDirectory %s"        %(self.paras.toMount(self.projectroot))
                cmd = cmd + " --outputFile %s"              %(self.paras.toMount(statetablefile))
                cmd = cmd + " --ribbon %d"                  %(self.ribbon)
                cmd = cmd + " --session %d"                 %(self.session)
                cmd = cmd + " --section %d"                 %(sectnum)
                cmd = cmd + " --oneribbononly True"

    		  #Run ====================
                self.submit(cmd)

class CreateRawDataRenderStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateRawDataRenderStacks")

    def run(self, sessionFolder):

        p = self.paras
        logger.info("Processing session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        rp     = p.renderProject

        for sectnum in range(p.firstSection, p.lastSection + 1):
            logger.info("Processing section: " + str(sectnum))

            #State table file
            statetablefile = p.getStateTableFileName(ribbon, session, sectnum)

            #upload acquisition stacks
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m renderapps.dataimport.create_fast_stacks_multi"
            cmd = cmd + " --render.host %s"           %rp.host
            cmd = cmd + " --render.owner %s "         %rp.owner
            cmd = cmd + " --render.project %s"        %rp.projectName
            cmd = cmd + " --render.client_scripts %s" %rp.clientScripts
            cmd = cmd + " --render.port %d"           %rp.hostPort
            cmd = cmd + " --render.memGB %s"          %rp.memGB
            cmd = cmd + " --log_level %s"             %rp.logLevel
            cmd = cmd + " --statetableFile %s"        %(self.paras.toMount(statetablefile))
            cmd = cmd + " --projectDirectory %s"      %(self.paras.toMount(projectroot))
            cmd = cmd + " --dataOutputFolder %s"      %(posixpath.join("." , p.dataOutputFolder.replace('\\', '/')))
            cmd = cmd + " --outputStackPrefix S%d_"   %(session)
            cmd = cmd + " --reference_channel %s"     %(p.referenceChannelRegistration)

            #Run =============
            self.submit(cmd)

class CreateMedianFiles(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateMedianFiles")

    def run(self, sessionFolder):
        p = self.paras
        logger.info("Creating median files for session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        #Output directories
        median_dir       = os.path.join("%s"%projectroot, p.dataOutputFolder, "medians")
        median_json      = os.path.join(median_dir, "median_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

        #Make sure output folder exist
        if os.path.isdir(median_dir) == False:
            os.mkdir(median_dir)

        #stacks
        acq_stack        = "S%d_Session%d"%(session, session)
        median_stack     = "S%d_Medians"%(session)

        rp               = p.renderProject

        with open(p.median_template) as json_data:
            med = json.load(json_data)

        u.savemedianjson(med, median_json, rp, acq_stack, median_stack, self.paras.toMount(median_dir), ribbon*100 + p.firstSection, ribbon*100 + p.lastSection, True)

        cmd = "docker exec " + p.atCoreContainer
        cmd = cmd + " python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(self.paras.toMount(median_json))

        #Run =============
        self.submit(cmd)

class CreateFlatFieldCorrectedData(atpp.PipelineProcess):
    def __init__(self, _paras):
        super().__init__(_paras, "CreateFlatFieldCorrectedData")

    def run(self, sessionFolder):
        p = self.paras
        logger.info("Processing session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        #Output directories
        flatfield_dir    = os.path.join(projectroot, p.dataOutputFolder, "flatfield")

        #Make sure output folder exists
        if os.path.isdir(flatfield_dir) == False:
           os.mkdir(flatfield_dir)

        #stacks
        acq_stack        = "S%d_Session%d"%(session,session)
        median_stack     = "S%d_Medians"%(session)
        flatfield_stack  = "S%d_FlatFielded"%(session)

        renderProject     = p.renderProject

        #Create json files and apply median.
        for sectnum in range(p.firstSection, p.lastSection + 1):

            with open(p.flatfield_template) as json_data:
                 ff = json.load(json_data)

            flatfield_json = os.path.join(flatfield_dir, "flatfield_%s_%s_%s_%d.json"%(renderProject.projectName, ribbon, session, sectnum))

            z = ribbon*100 + sectnum

            u.saveflatfieldjson(ff, flatfield_json, renderProject, acq_stack, median_stack, flatfield_stack, p.toMount(flatfield_dir), z, True)
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m rendermodules.intensity_correction.apply_multiplicative_correction"
            cmd = cmd + " --render.port 80"
            cmd = cmd + " --input_json %s"%(p.toMount(flatfield_json))

            #Run =============
            self.submit(cmd)

class CreateStitchedSections(atpp.PipelineProcess):
    def __init__(self, _paras):
        super().__init__(_paras, "CreateStitchedSections")

    def run(self, sessionFolder):
        p = self.paras
        logger.info("Processing session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        #Output directories
        stitching_dir    = os.path.join(projectroot, p.dataOutputFolder, "stitching")

        #Make sure output folder exist
        if os.path.isdir(stitching_dir) == False:
           os.mkdir(stitching_dir)

        #stacks
        flatfield_stack  = "S%d_FlatFielded"%(session)
        stitched_stack   = "S%d_Stitched"%(session)

        renderProject     = p.renderProject

    	#Create json files and start stitching...
        for sectnum in range(p.firstSection, p.lastSection + 1):

            with open(p.stitching_template) as json_data:
                 stitching_template = json.load(json_data)

            stitching_json = os.path.join(stitching_dir, "flatfield""_%s_%s_%d.json"%(ribbon, session, sectnum))
            z = ribbon*100 + sectnum

            u.savestitchingjson(stitching_template, stitching_json, renderProject, flatfield_stack, stitched_stack, z)

            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " java -cp /shared/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC"
            cmd = cmd + " --input_json %s"%(p.toMount(stitching_json))

            #Run =============
            self.submit(cmd)


class DropStitchingMistakes(atpp.PipelineProcess):
    def __init__(self, _paras):
        super().__init__(_paras, "DropStitchingMistakes")

    def run(self, sessionFolder):
        p = self.paras
        logger.info("Processing session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    	# output directories
        dropped_dir = os.path.join(projectroot, p.dataOutputFolder, "dropped")

    	# Make sure output folder exist
        if os.path.isdir(dropped_dir) == False:
           os.mkdir(dropped_dir)

    	# stacks
        acquisition_Stack       = "S%d_Session%d"    %(session, session)
        stitched_dapi_Stack     = "S%d_Stitched"     %(session)
        dropped_dapi_Stack      = "S%d_Stitched_Dropped" %(session)

        rp     = p.renderProject

        # command string
        cmd = "docker exec " + p.atCoreContainer
        cmd = cmd + " python -m renderapps.stitching.detect_and_drop_stitching_mistakes"
        cmd = cmd + " --render.owner %s"                        %(rp.owner)
        cmd = cmd + " --render.host %s"                         %(rp.host)
        cmd = cmd + " --render.project %s"                      %(rp.projectName)
        cmd = cmd + " --render.client_scripts %s"               %(rp.clientScripts)
        cmd = cmd + " --render.port %d"                         %(rp.hostPort)
        cmd = cmd + " --render.memGB %s"                        %(rp.memGB)
        cmd = cmd + " --log_level %s"                           %(rp.logLevel)
        cmd = cmd + " --prestitchedStack %s"                    %(acquisition_Stack)
        cmd = cmd + " --poststitchedStack %s"                   %(stitched_dapi_Stack)
        cmd = cmd + " --outputStack %s"                         %(dropped_dapi_Stack)
        cmd = cmd + " --jsonDirectory %s"                       %(p.toMount(dropped_dir))
        cmd = cmd + " --edge_threshold %d"                      %(p.edgeThreshold)
        cmd = cmd + " --pool_size %d"                           %(p.atCoreThreads)
        cmd = cmd + " --distance_threshold %d"                  %(p.distance)

        # Run =============
        self.submit(cmd)