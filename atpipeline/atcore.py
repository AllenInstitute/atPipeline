import json
import traceback
import os
import pathlib
import docker
import argparse
import logging
import sys
import renderapi
from atpipeline import at_atcore_arguments, at_logging, at_system_config, at_pipeline, at_docker_manager
from atpipeline import at_utils as u
from atpipeline.render_classes import at_simple_renderapi as rapi
logger = at_logging.create_logger('atPipeline')

from atpipeline.pipelines import at_rough_align_pipeline, at_stitching_pipeline, at_fine_align_pipeline, at_registration_pipeline
from atpipeline import __version__

def main():

    try:
        parser = argparse.ArgumentParser()
        at_atcore_arguments.add_arguments(parser)

        args = parser.parse_args()

        #If no arguments are supplied, show help and quit
        if len(sys.argv)==1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        system_config = at_system_config.ATSystemConfig(args, client = 'atcore')
        logger.setLevel(getattr(logging, args.loglevel))

        #What project to process?
        dataInfo = {}
        if args.data:
            args.data = os.path.abspath(args.data)
            if os.path.exists(args.data) == False:
                raise ValueError("The folderpath: %s don't exist"%(args.data))
            system_config.config['DATA_INPUT']['PROJECT_DATA_FOLDER'] = os.path.abspath(args.data)

            #Query atcore for any data processing information we may need to setup, such as Ribbon, session and section information
            if args.datasummary:
                cmd = 'docker exec ' + system_config.atcore_ctr_name + ' atcli --datasummary --data ' + system_config.toMount(args.data)
            else:
                cmd = 'docker exec ' + system_config.atcore_ctr_name + ' atcli --data ' + system_config.toMount(args.data)

            dataInfo = json.loads(u.getJSON(cmd))

            if args.pipeline == None:
                #print(json.dumps(dataInfo, indent=2, sort_keys=False))
                print (json.dumps(dataInfo, sort_keys=False))
                #print('\nPlease supply a valid pipeline to option "--pipeline" in order to process data.')
                return

        if args.deleterenderproject:
            if args.renderprojectowner is None:
                parser.error("--deleterenderproject flag requires --renderprojectowner to be set")
            else:
                r = rapi.SimpleRenderAPI(system_config)
                count = r.delete_stacks(args.renderprojectowner, args.deleterenderproject)
                print ("Deleted " + str(count) + " stacks")

                matchContexts =[args.deleterenderproject + "_HR_2D", args.deleterenderproject + "_HR_3D", args.deleterenderproject + "_lowres_round"]
                for c in matchContexts:
                    response = r.delete_match_context(args.renderprojectowner, c)
                    print('Delete match context response: ' + str(response))
                return

        if args.getprojectsbyowner:
            r = rapi.SimpleRenderAPI(system_config)
            projects = r.get_projects(args.getprojectsbyowner)
            print (projects)
            return

        if args.getstacksforproject:
            if args.renderprojectowner is None:
                parser.error("--getstacksforproject flag requires --renderprojectowner to be set")
            else:
                r = rapi.SimpleRenderAPI(system_config)
                stacks = r.get_stacks(args.renderprojectowner, args.getstacksforproject)
                print (stacks)
            return

        #All parameters are now well defined, copy them (and do some parsing) to a file where output data is written
        #The create rexieferences functions appends and overrides various arguments
        system_config.createReferences(args, data_info = dataInfo, client = "atcore")

        #Create data outputfolder and write processing parametrs to output folder
        if os.path.isdir(system_config.absoluteDataOutputFolder) == False:
            os.makedirs(system_config.absoluteDataOutputFolder)

        #Save current config values to the data output folder
        system_config.write(os.path.join(system_config.absoluteDataOutputFolder, system_config.project_name + '.ini'))

        if args.logtofile == True:
            logfilename = os.path.join(system_config.absoluteDataOutputFolder, system_config.project_name + '.log')
            at_logging.add_logging_to_file('atPipeline', logfilename)

        #Check which pipeline to run
        if system_config.pipeline == 'stitch':
            aPipeline = at_stitching_pipeline.Stitch(system_config)

        elif system_config.pipeline == 'roughalign':
            aPipeline = at_rough_align_pipeline.RoughAlign(system_config)

        elif system_config.pipeline == 'finealign':
            aPipeline = at_fine_align_pipeline.FineAlign(system_config)

        elif system_config.pipeline == 'register':
            aPipeline = at_registration_pipeline.RegisterSessions(system_config)

        elif system_config.pipeline == 'singletile':
            aPipeline = at_single_tile_data_pipeline.SingleTileData(system_config)
        else:
            logger.error('No such pipeline: "' + system_config.pipeline + '"')
            raise Exception('No such pipeline')

        #Run the pipeline
        aPipeline.run()

    except ValueError as e:
        logger.error('ValueError: ' + str(e))
        print(traceback.format_exc())

    except Exception as e:
        logger.error('Exception: ' + str(e))
        print(traceback.format_exc())

if __name__ == '__main__':
    main()
