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

def scriptArguments(caller = None):
    #Get processing parameters
    parser = argparse.ArgumentParser(prog = caller)
    parser.add_argument('--startall',            help='Start the whole AT backend',          action='store_true')
    parser.add_argument('--startbackend',        help='Start the whole backend',             action='store_true')
    parser.add_argument('--startrenderbackend',  help='Start the Render backend',            action='store_true')
    parser.add_argument('--killall',             help='Stop the AT backend',                 action='store_true')
    parser.add_argument('--prune_all',           help='Prune the AT backend',                action='store_true')
    parser.add_argument('--prune_containers',    help='Prune the AT backend',                action='store_true')
    parser.add_argument('--prune_images',        help='Prune the AT backend',                action='store_true')
    parser.add_argument('--restartall',          help="Restart all AT backend container",    action='store_true' )
    parser.add_argument('--status',              help="Get backend status",                  action='store_true' )

    parser.add_argument('-s', '--start',         help="Start a specific backend container, e.g. atcore",     nargs='?',const='atcore', type=str)
    parser.add_argument('-k', '--kill',          help='Stop a specific backend cointainer',                  nargs='?',const='atcore', type=str)
    parser.add_argument('-r', '--restart',       help="Restart a specific backend container, e.g. atcore",   nargs='?',const='atcore', type=str)
    return parser

def main():

    try:
        logger.info("============ Managing the atBackend =============")
        parser = scriptArguments("backend_management")
        args = parser.parse_args()

        parameters = at_system_config.ATSystemConfig(os.path.join("config", "SystemConfig.ini"))
        parameters.createReferences(parser)

        dManager = at_docker_manager.DockerManager()
        dManager.setupMounts(parameters.mounts, parameters.mountRenderPythonApps, parameters.mountRenderModules)
        dManager.setComposeFile(os.path.join("config", "docker-compose.yml"))

        if args.restart:
            dManager.reStartContainer(args.restart)

        elif args.start:
            dManager.startContainer(args.start)

        #---- render containers ??
        elif args.kill:
            dManager.stopContainer(args.stop)

        elif args.killall:
            dManager.killAllContainers()

        elif args.startall:
            #start the render backend first
            if dManager.startRenderBackend() == False:
                raise Exception("Failed starting the RenderBackend")

            #Start the atcore container
            dManager.startContainer("atcore")

        elif args.startrenderbackend:
            #start the render backend first
            if dManager.startRenderBackend() == False:
                raise Exception("Failed starting the RenderBackend")

        elif args.restartall:
            dManager.reStartAll()

        elif args.prune_images:
            dManager.prune_images()

        elif args.prune_containers:
            dManager.prune_containers()

        elif args.prune_all:
            dManager.prune_all()

        elif args.status:
            dManager.status()

    except ValueError as e:
        logger.error("ValueError: " + str(e))

    except Exception as e:
        logger.error("Exception: " + str(e))

if __name__ == '__main__':
    main()
