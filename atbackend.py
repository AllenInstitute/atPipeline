import os
import sys
import pathlib
import docker
import argparse
import traceback
import at_logging
logger = at_logging.create_logger('atPipeline')
import at_docker_manager
import at_system_config

def setupArguments(parser):
    #Get processing parameters
    parser.add_argument('--startall',            help='Start the whole AT backend',          action='store_true')
    parser.add_argument('--startbackend',        help='Start the whole backend',             action='store_true')
    parser.add_argument('--startrenderbackend',  help='Start the Render backend',            action='store_true')
    parser.add_argument('--killall',             help='Stop the AT backend',                 action='store_true')
    parser.add_argument('--prune_all',           help='Prune the AT backend',                action='store_true')
    parser.add_argument('--prune_containers',    help='Prune the AT backend',                action='store_true')
    parser.add_argument('--prune_images',        help='Prune the AT backend',                action='store_true')
    parser.add_argument('--restartall',          help='Restart all AT backend container',    action='store_true' )
    parser.add_argument('--status',              help='Get backend status',                  action='store_true' )

    parser.add_argument('-s', '--start',         help='Start a specific backend container, e.g. atcore',     nargs='?',const='atcore', type=str)
    parser.add_argument('-k', '--kill',          help='Stop a specific backend cointainer',                  nargs='?',const='atcore', type=str)
    parser.add_argument('-r', '--restart',       help='Restart a specific backend container, e.g. atcore',   nargs='?',const='atcore', type=str)

def main():

    try:
        logger.info('============ Managing the atBackend =============')

        dManager = at_docker_manager.DockerManager()

        #Keep arguments in main module for visibility
        setupArguments(dManager.argparser)
        args = dManager.parseCommandLineArguments()

        if args.restart:
            dManager.reStartContainer(args.restart)

        elif args.start:
            dManager.startContainer(args.start)

        elif args.kill:
            dManager.stopContainer(args.kill)

        elif args.killall:
            dManager.killAllContainers()

        elif args.startall:
            if dManager.startRenderBackend() == False:
                raise Exception('Failed starting the RenderBackend')

            #Start the atcore container
            dManager.startContainer('atcore')

        elif args.startrenderbackend:
            if dManager.startRenderBackend() == False:
                raise Exception('Failed starting the RenderBackend')

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
        logger.error('ValueError: ' + str(e))
        print(traceback.format_exc())

    except Exception as e:
        logger.error('Exception: ' + str(e))
        print(traceback.format_exc())

if __name__ == '__main__':
    main()
