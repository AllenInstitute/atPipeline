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

def setupScriptArguments():
    #Get processing parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-startAll', help='Start the whole AT backend',         action='store_true')
    parser.add_argument('-startRenderBackend', help='Start the Render backend', action='store_true')
    parser.add_argument('-killAll', help='Stop the AT backend', action='store_true')
    parser.add_argument("--restart", help="Restart a specific backend container, e.g. atcore")
    parser.add_argument("--start", help="Start a specific backend container, e.g. atcore")
    parser.add_argument('--stop', help='Stop a specific backend cointainer')
    return parser.parse_args()

def main():

    logger.info("============ Managing the atBackend =============")
    args = setupScriptArguments()

    atCoreCtrName="atcore"

    cwd = pathlib.Path().absolute().resolve()

    dManager = at_docker_manager.DockerManager()

    #TODO: put this in H/W config file
    atCoreMounts = {
        'c:\data'                                        : {'bind': '/data_mount_1', 'mode' : 'rw'},
        os.path.join(cwd, 'pipeline')                    : {'bind' : '/pipeline', 'mode' : 'ro'},
#        os.path.join(cwd, 'docker', 'render-python-apps')   : {'bind': '/shared/render-python-apps'},
#        os.path.join(cwd, 'docker', 'render-modules')       : {'bind': '/shared/render-modules'}
    }

    #docker compose file
    composeFile = os.path.join(cwd, "docker-compose.yml")

    try:
        if args.restart:
            dManager.reStartContainer(atCoreCtrName, atCoreMounts)

        if args.start:
            dManager.startContainer(atCoreCtrName, atCoreMounts)

        #---- render containers ??
        if args.stop:
            if args.stop == atCoreCtrName:
                if dManager.stopContainer(atCoreCtrName) == True:
                    logger.info("Stopped atcore container")
                else:
                    logger.error("Failed stopping container")

        if args.killAll:
            dManager.killAllContainers()

        if args.startAll:
            #start the render backend first
            if dManager.startRenderBackend(composeFile) == False:
                raise Exception("Failed starting the RenderBackend")

            #Start the atcore container
            dManager.startContainer("atcore", atCoreMounts)

        if args.startRenderBackend:
            #start the render backend first
            if dManager.startRenderBackend(composeFile) == False:
                raise Exception("Failed starting the RenderBackend")

    except ValueError as e:
        logger.error("ValueError: " + str(e))

    except Exception as e:
        logger.error("Exception: " + str(e))


if __name__ == '__main__':
    main()
