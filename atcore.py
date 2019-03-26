import at_logging
logger = at_logging.setup_custom_logger('atPipeline')
import os
import pathlib
import docker
import argparse
import at_docker_manager
from source import *
import source.atutils as u
import at_system_config
import atpipeline
import json

def scriptArguments():
    #Get processing parameters
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    #Required arguments
    required.add_argument('--datainput',            help='Full path to data folder for project data to process',                type=str,   nargs='?',                          required=True)

    required.add_argument('--pipeline',             help='Specify the pipeline to use, e.g. stitch, finealign or register. \
                                                                                                     Default = \'stitch\'',     type=str,   nargs='?',      const='stitch'    )

    #Optional arguments
    optional.add_argument('--renderprojectowner',   help='Specify a RenderProject owner',                                       type=str,   nargs='?')
    optional.add_argument('--sessions',             help='Specify sessions to process',                                         type=str)
    optional.add_argument('--ribbons',              help='Specify ribbons  to process',                                         type=str)
    optional.add_argument('--firstsection',         help='Specify start section',                                               type=int)
    optional.add_argument('--lastsection',          help='Specify end section',                                                 type=int)
    optional.add_argument('--overwritedata',        help='Overwrite any already processed data',                                action='store_true')
    return parser.parse_args(), parser

def main():

    try:
        cwd = pathlib.Path().absolute().resolve()
        system_parameters = at_system_config.ATSystemConfig(os.path.join("config", "SystemConfig.ini"))
        logger.info("============ ATCORE ============")
        args,parser = scriptArguments()

        #What project to process?
        if args.datainput:
            system_parameters.config['DATA_INPUT']['PROJECT_DATA_FOLDER'] = args.datainput


        if args.datainput and not args.pipeline:
            print ("Supply a valid pipeline name to --pipeline. Valid pipelines are stitch, align and register")
            return

        #Query atcore for any data processing information we may need to setup, such as Ribbon, session and section information
        cmd = "docker exec clang atcore --json --dataroot " + system_parameters.toMount(args.datainput)
        dataInfo = json.loads(u.getJSON(cmd))

        #All parameters are now well defined, copy them (and do some parsing) to a file where output data is written
        #The create references functions appends and overrides various arguments
        system_parameters.createReferences(args, dataInfo)


        #Create data outputfolder and write processing parametrs to output folder
        if os.path.isdir(system_parameters.dataOutputFolder) == False:
            os.makedirs(system_parameters.dataOutputFolder)

        system_parameters.write(os.path.join(system_parameters.dataOutputFolder, system_parameters.projectName + ".ini"))

        #Check which pipeline to run
        if system_parameters.pipeline == "stitch":
            logger.info("Running stitching pipeline")
            aPipeline = atpipeline.Stitch(system_parameters)
        else:
            logger.error("No such pipeline: " + system_parameters.pipeline)
            raise Exception("No such pipeline")

        #Run the pipeline
        aPipeline.run()

    except ValueError as e:
        logger.error("ValueError: " + str(e))

    except Exception as e:
        logger.error("Exception: " + str(e))


if __name__ == '__main__':
    main()
