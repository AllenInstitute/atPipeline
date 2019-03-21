import at_logging
logger = at_logging.setup_custom_logger('atPipeline')
import os
import sys
import timeit
import pathlib
import docker
import argparse
import at_docker_manager
from source import *
import source.atutils as u
import ast
import at_system_config
import atpipeline

def scriptArguments():
    #Get processing parameters
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('--project',              help='Full path to data folder for project data to process',                nargs='?',  type=str, required=True)
    required.add_argument('--pipeline',             help='Specify the pipeline to use, e.g. stitch, finealign or register',     nargs='?',  const='stitch',    type=str)

    optional.add_argument('--sessions',             help='Specify sessions to process',                             type=str)
    optional.add_argument('--ribbons',              help='Specify ribbons  to process',                             type=str)
    optional.add_argument('--firstsection',         help='Specify start section',                                   type=int)
    optional.add_argument('--lastsection',          help='Specify end section',                                     type=int)
    optional.add_argument('--renderprojectowner',   help='Specify  RP owner',                                       type=str)
#    optional.add_argument('--overwritedata',            help='Overwrites any already processed data',               type=bool, nargs='?', const=False, required = True)

    return parser.parse_args(), parser

def main():

    try:
        cwd = pathlib.Path().absolute().resolve()
        system_parameters = at_system_config.ATSystemConfig(os.path.join("config", "SystemConfig.ini"))
        logger.info("============ ATCORE ============")
        args,parser = scriptArguments()

        #What project to process?
        if args.project:
            system_parameters.config['DATA_INPUT']['PROJECT_DATA_FOLDER'] = args.project

        if args.project and not args.pipeline:
            cmd = "docker exec -t clang atcli --json --dataroot " + system_parameters.toDockerMountedPath(args.project)
            u.runShellCMD(cmd)
            logger.info("Return information about input data, e.g. number of sessions, sections and ribbons")
            return

        #All parameters are now well defined, copy them (and do some parsing) to a file where output data is written
        #The create references functions appends and overrides various arguments
        system_parameters.createReferences(args)

        #Create data outputfolder
        if os.path.isdir(system_parameters.dataOutputFolder) == False:
            os.mkdir(system_parameters.dataOutputFolder)

        system_parameters.write(os.path.join(system_parameters.dataOutputFolder, system_parameters.projectName + ".ini"))
        aPipeline = None

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
