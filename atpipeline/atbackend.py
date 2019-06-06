import os
import sys
import pathlib
import docker
import argparse
import traceback
from atpipeline import at_logging, at_docker_manager, at_system_config
logger = at_logging.create_logger('atPipeline')
from atpipeline import __version__
from atpipeline import at_backend_arguments

def main():

    try:
        logger.info('============ Managing the atBackend =============')

        parser = argparse.ArgumentParser('atbackend')
        at_backend_arguments.add_arguments(parser)
        args = parser.parse_args()

        system_config = at_system_config.ATSystemConfig(args, client = 'atbackend')

        dManager = at_docker_manager.DockerManager(system_config)

        if args.restart:
            dManager.reStartContainer(args.restart)

        elif args.start:
            dManager.startContainer(args.start)

        elif args.kill:
            dManager.stopContainer(args.kill)

        elif args.killall:
            dManager.killAllContainers(args.killall)

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

        elif args.pruneimages:
            dManager.prune_images()

        elif args.prunecontainers:
            dManager.prune_containers()

        elif args.pruneall:
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
