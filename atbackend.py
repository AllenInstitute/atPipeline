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

def scriptArguments():
    #Get processing parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--startAll',            help='Start the whole AT backend',          action='store_true')
    parser.add_argument('--startRenderBackend',  help='Start the Render backend',            action='store_true')
    parser.add_argument('--killAll',             help='Stop the AT backend',                 action='store_true')
    parser.add_argument('-ra', '--restartAll',   help="Restart all AT backend container",    action='store_true' )

    parser.add_argument('-s', '--start',         help="Start a specific backend container, e.g. atcore",     nargs='?',const='atcore', type=str)
    parser.add_argument('-k', '--kill',          help='Stop a specific backend cointainer',                  nargs='?',const='atcore', type=str)
    parser.add_argument('-r', '--restart',       help="Restart a specific backend container, e.g. atcore",   nargs='?',const='atcore', type=str)

    return parser.parse_args()

def main():

    try:
        parameters = at_system_config.ATSystemConfig("SystemConfig.ini")
        parameters.createReferences()
        logger.info("============ Managing the atBackend =============")
        args = scriptArguments()

        atCoreCtrName="atcore"

        cwd = pathlib.Path().absolute().resolve()

        dManager = at_docker_manager.DockerManager()
        dManager.setupMounts(parameters.dataRoots, parameters.mountRenderPythonApps, parameters.mountRenderModules)
        dManager.setComposeFile(os.path.join(cwd, "docker-compose.yml"))

        if args.restart:
            dManager.reStartContainer(args.restart)

        elif args.start:
            dManager.startContainer(args.start)

        #---- render containers ??
        elif args.kill:
            dManager.stopContainer(args.stop)

        elif args.killAll:
            dManager.killAllContainers()

        elif args.startAll:
            #start the render backend first
            if dManager.startRenderBackend() == False:
                raise Exception("Failed starting the RenderBackend")

            #Start the atcore container
            dManager.startContainer("atcore")

        elif args.startRenderBackend:
            #start the render backend first
            if dManager.startRenderBackend() == False:
                raise Exception("Failed starting the RenderBackend")

        elif args.restartAll:
            dManager.reStartAll()


    except ValueError as e:
        logger.error("ValueError: " + str(e))

    except Exception as e:
        logger.error("Exception: " + str(e))


if __name__ == '__main__':
    main()
