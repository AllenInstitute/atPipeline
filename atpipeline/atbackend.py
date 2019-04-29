import os
import sys
import pathlib
import docker
import argparse
import traceback
from . import at_logging, at_docker_manager, at_system_config
logger = at_logging.create_logger('atPipeline')
from . import __version__

def setupArguments(parser):
    #Get processing parameters
    cmdgroup = parser.add_mutually_exclusive_group()
    cmdgroup.add_argument('--startall',            help='Start the whole AT backend',          action='store_true')
    cmdgroup.add_argument('--startrenderbackend',  help='Start the Render backend',            action='store_true')
    cmdgroup.add_argument('--killall', '--stopall', help='Stop the AT backend',                 action='store_true')
    cmdgroup.add_argument('--prune_all',           help='Prune the AT backend',                action='store_true')
    cmdgroup.add_argument('--prune_containers',    help='Prune the AT backend',                action='store_true')
    cmdgroup.add_argument('--prune_images',        help='Prune the AT backend',                action='store_true')
    cmdgroup.add_argument('--restartall',          help='Restart all AT backend container',    action='store_true' )
    cmdgroup.add_argument('--status',              help='Get backend status',                  action='store_true' )

    cmdgroup.add_argument('-s', '--start',         help='Start a specific backend container, e.g. atcore',     nargs='?',const='atcore', type=str)
    cmdgroup.add_argument('-k', '--kill',          help='Stop a specific backend cointainer',                  nargs='?',const='atcore', type=str)
    cmdgroup.add_argument('-r', '--restart',       help='Restart a specific backend container, e.g. atcore',   nargs='?',const='atcore', type=str)

    # Flags to alter behaviour
    parser.add_argument('--atcore_image', help='Name of atcore image to use', default='atpipeline/atcore:dev')
    parser.add_argument('--config_folder', help='Path to config folder', default=None)

    parser.add_argument('--define', '-D',
        action='append',
        default=[],
        help="Override a value in the config file (-D section.item=value)")

    parser.add_argument('--version', '-v', action='version', version=('%%(prog)s %s' % __version__))
    
def main():

    try:
        logger.info('============ Managing the atBackend =============')
        
        parser = argparse.ArgumentParser()
        setupArguments(parser)
        args = parser.parse_args()

        dManager = at_docker_manager.DockerManager(configFolder=args.config_folder,
                        atcore_image=args.atcore_image,
                        cmdFlags=args.define)

        #Keep arguments in main module for visibility
        #setupArguments(dManager.argparser)
        #args = dManager.parseCommandLineArguments()

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
