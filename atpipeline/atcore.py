import json
import traceback
import os
import pathlib
import docker
import argparse
import logging
from atpipeline import at_logging, at_system_config, at_pipeline, at_docker_manager
from atpipeline import at_utils as u
logger = at_logging.create_logger('atPipeline')
from atpipeline.pipelines import at_rough_align_pipeline, at_stitching_pipeline, at_fine_align_pipeline, at_registration_pipeline
from atpipeline import __version__

def parseArguments(parser):
    parser.add_argument('--configfolder',
        metavar="PATH",
        help='Path to config folder',
        default=None)

    parser.add_argument('--configfilename',
        metavar="PATH",
        help='Name of config file, may include the path',
        default="at-system-config.ini")

    parser.add_argument('--data',
        metavar="PATH",
        help='Full path to data folder for project data to process',
        required=True)

    parser.add_argument('--projectname',
        help='Set project name. Default: name of input datas basefolder',
        required=False)

    parser.add_argument('--pipeline',
        help='Specify the pipeline to use',
        choices={'stitch', 'roughalign', 'finealign', 'register'},
        required=False)

    parser.add_argument('--renderprojectowner',
        help='Specify a RenderProject owner',
        metavar="OWNER",
        type=str,
        nargs='?')

    parser.add_argument('--sessions',
        help='Specify sessions to process',
        type=str)

    parser.add_argument('--ribbons',
        help='Specify ribbons  to process',
        type=str)

    parser.add_argument('--firstsection', metavar='N',
        help='Specify start section (e.g. \'1\' to start with a datasets first section)',
        type=int)

    parser.add_argument('--lastsection', metavar='N',
    help='Specify end section',
    type=int)

    parser.add_argument('--overwritedata',
        help='Overwrite any already processed data',
        action='store_true')

    parser.add_argument('--singletiledata',
        help='Set this one if sections only contain one tile',
        action='store_true')

    parser.add_argument('--loglevel',
        choices={'INFO', 'DEBUG', 'WARNING', 'ERROR'},
        help='Set program loglevel',
        default='INFO')

    parser.add_argument('--logtofile',
        help='Log messages to file. The logfile is written to the output datafolder and named "projectname".log',
        action='store_true')

    parser.add_argument('--define', '-D',
        action='append',
        default=[],
        help="Override a value in the config file (-D section.item=value)")

    parser.add_argument('--version', '-v', action='version', version=('%%(prog)s %s' % __version__))

def main():
    parser = argparse.ArgumentParser()
    parseArguments(parser)
    args = parser.parse_args()

    try:
        if args.configfolder:
            configFolder = args.configfolder
        elif 'AT_SYSTEM_CONFIG_FOLDER' in os.environ:
            configFolder = os.environ['AT_SYSTEM_CONFIG_FOLDER']
        elif os.name == 'posix':
            configFolder = '/usr/local/etc/'
        else:
            raise Exception("No default configFolder folder defined for %s. Set environment variable 'AT_SYSTEM_CONFIG_FOLDER' to the folder where the file 'at-system-config.ini' exists." % os.name)

        if os.path.exists(args.configfilename):
            args.configfilename = os.path.abspath(args.configfilename)
            system_parameters = at_system_config.ATSystemConfig(args.configfilename)
        else:
        	system_parameters = at_system_config.ATSystemConfig(os.path.join(configFolder, args.configfilename),
                                cmdFlags=args.define)

        logger.setLevel(getattr(logging, args.loglevel))

        #What project to process?
        if args.data:
            args.data = os.path.abspath(args.data)
            system_parameters.config['DATA_INPUT']['PROJECT_DATA_FOLDER'] = os.path.abspath(args.data)

        if args.data and not args.pipeline:
            lvl = logger.getEffectiveLevel()
            lvlName = logging.getLevelName(lvl)
            cmd = 'docker exec atcore atcli --json --dataroot ' + system_parameters.toMount(args.data)
            lines = u.runShellCMD(cmd, True)
            for line in lines:
                print (line.rstrip())

            return

        #Query atcore for any data processing information we may need to setup, such as Ribbon, session and section information
        cmd = 'docker exec atcore atcli --json --dataroot ' + system_parameters.toMount(args.data)
        dataInfo = json.loads(u.getJSON(cmd))

        #All parameters are now well defined, copy them (and do some parsing) to a file where output data is written
        #The create references functions appends and overrides various arguments
        system_parameters.createReferences(args, "pipeline", dataInfo)

        #Create data outputfolder and write processing parametrs to output folder
        if os.path.isdir(system_parameters.absoluteDataOutputFolder) == False:
            os.makedirs(system_parameters.absoluteDataOutputFolder)

        #Save current config values to the data output folder
        system_parameters.write(os.path.join(system_parameters.absoluteDataOutputFolder, system_parameters.project_name + '.ini'))

        if args.logtofile == True:
            logfilename = os.path.join(system_parameters.absoluteDataOutputFolder, system_parameters.project_name + '.log')
            at_logging.add_logging_to_file('atPipeline', logfilename)

        #Check which pipeline to run
        if system_parameters.pipeline == 'stitch':
            aPipeline = at_stitching_pipeline.Stitch(system_parameters)

        elif system_parameters.pipeline == 'roughalign':
            aPipeline = at_rough_align_pipeline.RoughAlign(system_parameters)

        elif system_parameters.pipeline == 'finealign':
            aPipeline = at_fine_align_pipeline.FineAlign(system_parameters)

        elif system_parameters.pipeline == 'register':
            aPipeline = at_registration_pipeline.RegisterSessions(system_parameters)

        else:
            logger.error('No such pipeline: "' + system_parameters.pipeline + '"')
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
