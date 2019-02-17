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
    parser.add_argument('-startAll', help='Start the AT backend', action='store_true')
    parser.add_argument('-killAll', help='Stop the AT backend', action='store_true')
    parser.add_argument("--start", help="Start a specific backend container, e.g. atcore")
    parser.add_argument('--stop', help='Stop a specific backend cointainer')
    return parser.parse_args()

def main():

    logger.info("============ Managing the atBackend =============")
    args = setupScriptArguments()
    atCoreCtrName="atcore"
    renderServices="atcore"

    cwd = 'c:\\pDisk\\atPipeline'

    dManager = at_docker_manager.DockerManager()
    atCoreMounts = {
        '/c/data'                                           : {'bind': '/mnt'},
        os.path.join(cwd, 'pipeline')                       : {'bind': '/pipeline'},
        os.path.join(cwd, 'docker', 'render-python-apps')   : {'bind': '/shared/render-python-apps'},
        os.path.join(cwd, 'docker', 'render-modules')       : {'bind': '/shared/render-modules'}
    }
    try:

        if args.start:
            if args.start == atCoreCtrName:
                if dManager.startContainer(atCoreCtrName, atCoreMounts) == True:
                    logger.info("Started atcore container")
                else:
                    logger.error("Failed starting container")
            #---- render containers

        if args.stop:
            if args.stop == atCoreCtrName:
                if dManager.stopContainer(atCoreCtrName) == True:
                    logger.info("Stopped atcore container")
                else:
                    logger.error("Failed stopping container")

        if args.killAll:
            dManager.killAllContainers()


    except ValueError as error:
        print ("A value error occured: " + str(error))

    except Exception as e:
        print ("An error occured..")
        print (e)


if __name__ == '__main__':
    main()
