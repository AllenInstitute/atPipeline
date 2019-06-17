import os
import logging
import json
import renderapi
from .. import at_pipeline as atp
from .. import at_pipeline_process as atpp
from atpipeline.render_classes import at_simple_renderapi as srapi
from atpipeline import at_utils as u
import posixpath

logger = logging.getLogger('atPipeline')

class Stitch(atp.ATPipeline):
    def __init__(self, _paras):
        super().__init__(_paras)

        #Define the pipeline
        self.append_pipeline_process(CreateStateTables(_paras))
        self.append_pipeline_process(CreateRawDataRenderStacks(_paras))
        self.append_pipeline_process(CreateMedianFiles(_paras))
        self.append_pipeline_process(CreateFlatFieldCorrectedData(_paras))
        self.append_pipeline_process(CreateStitchedSections(_paras))
        self.append_pipeline_process(DropStitchingMistakes(_paras))

    def run(self):
        atp.ATPipeline.run(self)
        return True


##Sub processes in the stitching pipeline are defined below

#Creation of statetables are done session by session, ribbon by ribbon and finally, by section
class CreateStateTables(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateStateTables")

    #def check_if_done(self):
        #Query render for stack metadata for each session
        #If stacks exists, then don't create new ones, unless overwrite data is True
        #Optionally, check existence of raw data as well
        #for sessionFolder in self.sessionFolders:
    #    pass

    #def validate(self):
    #    pass

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:
            logger.info("=========== Creating state tables for session: " + sessionFolder + " ===============")

            #Check which ribbon we are processing, and adjust section numbers accordingly
            ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(ribbon)
            [project_root, ribbon, session] = u.parse_session_folder(sessionFolder)

            for sectnum in range(firstSection, lastSection + 1):
                logger.debug("Processing section: " + str(sectnum))

                #State table file
                statetablefile = self.paras.getStateTableFileName(ribbon, session, sectnum)
                logger.info("Creating statetable file: " + statetablefile)

                cmd =       "/opt/conda/bin/python /pipeline/make_state_table_ext_multi_pseudoz.py"
                cmd = cmd + " --projectDirectory %s"        %(p.toMount(project_root))
                cmd = cmd + " --outputFile %s"              %(p.toMount(statetablefile))
                cmd = cmd + " --ribbon %d"                  %(ribbon)
                cmd = cmd + " --session %d"                 %(session)
                cmd = cmd + " --section %d"                 %(sectnum)
                cmd = cmd + " --oneribbononly True"

		        #Run ====================
                self.submit_atcore(cmd)

class CreateRawDataRenderStacks(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateRawDataRenderStacks")

    #def check_if_done(self):
        #Query render for stack metadata for each session
        #If stacks exists, then don't create new ones, unless overwrite data is True
        #Optionally, check existence of raw data as well
        #for sessionFolder in self.sessionFolders:
    #    pass


    def run(self):
        super().run()
        p = self.paras
        for sessionFolder in self.sessionFolders:

            logger.info("Processing session folder: " + sessionFolder)
            [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

            rp     = p.renderProject

            #Check which ribbon we are processing, and adjust section numbers accordingly
            current_ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)

            for sectnum in range(firstSection, lastSection + 1):
                logger.info("Processing section: " + str(sectnum))

                #State table file
                statetablefile = p.getStateTableFileName(ribbon, session, sectnum)

                #upload acquisition stacks
                cmd =       "/opt/conda/bin/python -m renderapps.dataimport.create_fast_stacks_multi"
                cmd = cmd + " --render.host %s"           %rp.host
                cmd = cmd + " --render.owner %s "         %rp.owner
                cmd = cmd + " --render.project %s"        %rp.project_name
                cmd = cmd + " --render.client_scripts %s" %rp.clientScripts
                cmd = cmd + " --render.port %d"           %rp.hostPort
                cmd = cmd + " --render.memGB %s"          %rp.memGB
                cmd = cmd + " --log_level %s"             %rp.logLevel
                cmd = cmd + " --statetableFile %s"        %(p.toMount(statetablefile))
                cmd = cmd + " --projectDirectory %s"      %(p.toMount(projectroot))
                cmd = cmd + " --dataOutputFolder %s"      %(posixpath.join("." , p.dataOutputFolder.replace('\\', '/')))
                cmd = cmd + " --outputStackPrefix S%d_"   %(session)
                cmd = cmd + " --reference_channel %s"     %(p.referenceChannelRegistration)

                #Run =============
                self.submit_atcore(cmd)

#Medians are calculated on a ribbon by ribbon bases
class CreateMedianFiles(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateMedianFiles")

    def savemedianjson(self, template, outFile, render_project, acq_stack, median_stack, median_dir, minz, maxz, close_stack):
        template['render']['host']    = render_project.host
        template['render']['owner']   = render_project.owner
        template['render']['project'] = render_project.project_name
        template['input_stack']       = acq_stack
        template['output_stack']      = median_stack
        template['minZ']              = minz
        template['maxZ']              = maxz
        template['output_directory']  = median_dir
        template['close_stack']       = close_stack
        u.dump_json(template, outFile)

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:

            logger.info("Creating median files for session folder: " + sessionFolder)
            [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

            #Check which ribbon we are processing, and adjust section numbers accordingly
            current_ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)

            #Output directories
            median_dir       = os.path.join("%s"%projectroot, p.dataOutputFolder, "medians")
            median_json      = os.path.join(median_dir, "median_%s_%s_%d_%d.json"%(ribbon, session, firstSection, lastSection))

            #Make sure output folder exist
            if os.path.isdir(median_dir) == False:
                os.mkdir(median_dir)

            #stacks
            acq_stack        = "S%d_Session%d"%(session, session)
            median_stack     = "S%d_Medians"%(session)

            rp               = p.renderProject

            with open(p.median_template) as json_data:
                med = json.load(json_data)

            self.savemedianjson(med, median_json, rp, acq_stack, median_stack, self.paras.toMount(median_dir), ribbon*100 + firstSection, ribbon*100 + lastSection, True)

            cmd =       "/opt/conda/bin/python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
            cmd = cmd + " --render.port %d"           %rp.hostPort
            cmd = cmd + " --input_json %s"%(self.paras.toMount(median_json))

            #Run =============
            self.submit_atcore(cmd)

    #def check_if_done(self):
    #    pass

class CreateFlatFieldCorrectedData(atpp.PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateFlatFieldCorrectedData")

    def saveflatfieldjson(self, template, outFile, render_project, acq_stack, median_stack, flatfield_stack, flatfield_dir, sectnum, close_stack):
        template['render']['host']    = render_project.host
        template['render']['owner']   = render_project.owner
        template['render']['project'] = render_project.project_name
        template['input_stack']       = acq_stack
        template['correction_stack']  = median_stack
        template['output_stack']      = flatfield_stack
        template['z_index']           = sectnum
        template['output_directory']  = flatfield_dir
        template['close_stack']       = close_stack
        u.dump_json(template, outFile)


    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:

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
            #Check which ribbon we are processing, and adjust section numbers accordingly
            current_ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)

            for sectnum in range(firstSection, lastSection + 1):

                with open(p.flatfield_template) as json_data:
                     ff = json.load(json_data)

                flatfield_json = os.path.join(flatfield_dir, "flatfield_%s_%s_%s_%d.json"%(renderProject.project_name, ribbon, session, sectnum))

                z = ribbon*100 + sectnum

                self.saveflatfieldjson(ff, flatfield_json, renderProject, acq_stack, median_stack, flatfield_stack, p.toMount(flatfield_dir), z, True)
                cmd =       "/opt/conda/bin/python -m rendermodules.intensity_correction.apply_multiplicative_correction"
                cmd = cmd + " --render.port %d"           % renderProject.hostPort
                cmd = cmd + " --input_json %s"%(p.toMount(flatfield_json))

                #Run =============
                self.submit_atcore(cmd)

    #def check_if_done(self):
    #    pass

class CreateStitchedSections(atpp.PipelineProcess):
    def __init__(self, _paras):
        super().__init__(_paras, "CreateStitchedSections")

    def savestitchingjson(self, template, outfile, render_project, flatfield_stack, stitched_stack, sectnum):
        template['baseDataUrl']            = "http://%s/render-ws/v1"%(render_project.host)
        template['owner']                  = render_project.owner
        template['project']                = render_project.project_name
        template['stack']                  = flatfield_stack
        template['outputStack']            = stitched_stack
        template['section']                = sectnum
        u.dump_json(template, outfile)

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:

            logger.info("Processing session folder: " + sessionFolder)
            [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

            #Output directories
            stitching_dir    = os.path.join(projectroot, p.dataOutputFolder, "stitching")

            #Make sure output folder exist
            if os.path.isdir(stitching_dir) == False:
               os.mkdir(stitching_dir)

            #stacks
            input_stack  = "S%d_FlatFielded"%(session)
            output_stack   = "S%d_Stitched"%(session)

            #Check which ribbon we are processing, and adjust section numbers accordingly
            current_ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)

        	#Create json files and start stitching...
            for sectnum in range(firstSection, lastSection + 1):

                #Stitching is needed if the section have more than one tile
                nr_of_tiles_in_section = u.get_number_of_physical_tiles_in_section(sectnum, current_ribbon, p.dataInfo)
                z = ribbon*100 + sectnum
                if nr_of_tiles_in_section > 1:
                    with open(p.stitching_template) as json_data:
                         stitching_template = json.load(json_data)

                    stitching_json = os.path.join(stitching_dir, "stitched""_%s_%s_%d.json"%(ribbon, session, sectnum))


                    self.savestitchingjson(stitching_template, stitching_json, p.renderProject, input_stack, output_stack, z)

                    cmd =       "java -cp /shared/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC"
                    cmd = cmd + " --input_json %s"%(p.toMount(stitching_json))

                    #Run =============
                    self.submit_atcore(cmd)
                else:
                    rp     = p.renderProject
                    sr = srapi.SimpleRenderAPI(p, rp.owner)
                    #Create the output stack if it does not exist
##                    response = renderapi.stack.create_stack(output_stack,
##                                                            host="http://" + rp.host,
##                                                            owner=rp.owner,
##                                                            project=rp.project_name,
##                                                            render=sr.get_render_client())
##
##
##
##                    one_tile = renderapi.resolvedtiles.get_resolved_tiles_from_z(input_stack, z, project=rp.project_name, render=sr.get_render_client())
##                    response = renderapi.resolvedtiles.put_tilespecs(output_stack, one_tile, project=rp.project_name, render=sr.get_render_client())
##                    if response != 200:
##                        raise ValueError('Failed uploading tiles..')
                    response = renderapi.stack.clone_stack(input_stack, output_stack, owner=rp.owner, project=rp.project_name,  render=sr.get_render_client())
                    break
                    #just save the tile to output stack


    #def check_if_done(self):
    #    pass

class DropStitchingMistakes(atpp.PipelineProcess):
    def __init__(self, _paras):
        super().__init__(_paras, "DropStitchingMistakes")

    def run(self):
        super().run()
        p = self.paras

        for sessionFolder in self.sessionFolders:
            logger.info("Processing session folder: " + sessionFolder)
            [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        	# output directories
            dropped_dir = os.path.join(projectroot, p.dataOutputFolder, "dropped")

        	# Make sure output folder exist
            if os.path.isdir(dropped_dir) == False:
               os.mkdir(dropped_dir)

        	# stacks
            acquisition_Stack       = "S%d_Session%d"       %(session, session)
            stitched_dapi_Stack     = "S%d_Stitched"        %(session)
            dropped_dapi_Stack      = "S%d_Stitched_Dropped"%(session)

            rp     = p.renderProject

            #Check which ribbon we are processing, and adjust section numbers accordingly
            current_ribbon = u.getRibbonLabelFromSessionFolder(sessionFolder)
            firstSection, lastSection = p.convertGlobalSectionIndexesToCurrentRibbon(current_ribbon)

            nr_of_tiles_in_section = u.get_number_of_physical_tiles_in_section(firstSection, current_ribbon, p.dataInfo)

            if nr_of_tiles_in_section > 1:

                # command string
                cmd =       " /opt/conda/bin/python -m renderapps.stitching.detect_and_drop_stitching_mistakes"
                cmd = cmd + " --render.owner %s"                        %(rp.owner)
                cmd = cmd + " --render.host %s"                         %(rp.host)
                cmd = cmd + " --render.project %s"                      %(rp.project_name)
                cmd = cmd + " --render.client_scripts %s"               %(rp.clientScripts)
                cmd = cmd + " --render.port %d"                         %(rp.hostPort)
                cmd = cmd + " --render.memGB %s"                        %(rp.memGB)
                cmd = cmd + " --log_level %s"                           %(rp.logLevel)
                cmd = cmd + " --prestitchedStack %s"                    %(acquisition_Stack)
                cmd = cmd + " --poststitchedStack %s"                   %(stitched_dapi_Stack)
                cmd = cmd + " --outputStack %s"                         %(dropped_dapi_Stack)
                cmd = cmd + " --jsonDirectory %s"                       %(p.toMount(dropped_dir))

                cmd = cmd + " --edge_threshold %s"                      %(p.DROP_STITCHING_MISTAKES['EDGE_THRESHOLD'])
                cmd = cmd + " --pool_size %s"                           %(p.DROP_STITCHING_MISTAKES['POOL_SIZE'])
                cmd = cmd + " --distance_threshold %s"                  %(p.DROP_STITCHING_MISTAKES['DISTANCE_THRESHOLD'])

                # Run =============
                self.submit_atcore(cmd)
            else:
                rp     = p.renderProject
                sr = srapi.SimpleRenderAPI(p, rp.owner)

                #Create the output stack if it does not exist
                response = renderapi.stack.clone_stack(stitched_dapi_Stack, dropped_dapi_Stack, owner=rp.owner, project=rp.project_name,  render=sr.get_render_client())


    #def check_if_done(self):
    #    pass
