import at_logging
logger = at_logging.setup_custom_logger('atPipeline')
import os
import sys
import timeit
import pathlib
import docker
import argparse
import at_docker_manager
import subprocess
from source import *
import source.atutils as u

def setupScriptArguments():
    #Get processing parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-startAll', help='Start the whole AT backend', action='store_true')
    parser.add_argument('-killAll', help='Stop the AT backend', action='store_true')
    parser.add_argument("--start", help="Start a specific backend container, e.g. atcore")
    parser.add_argument('--stop', help='Stop a specific backend cointainer')
    return parser.parse_args()

def startRenderBackend(composeFile):

    if os.path.exists(composeFile) == False:
        raise Exception("The docker compose file: " + composeFile + " don't exist!")

    cmd = "docker-compose -f " + str(composeFile)
    cmd = cmd + " up -d"
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    return True

def main():

    logger.info("============ Managing the atBackend =============")
    args = setupScriptArguments()
    atCoreCtrName="atcore"
    renderServices="atcore"

    cwd = pathlib.Path().absolute().resolve()

    dManager = at_docker_manager.DockerManager()

    #TODO: put this in H/W config file
    atCoreMounts = {
        '/c/data'                                           : {'bind': '/data_input_mount_1'},
        '/c/data/data_output'                               : {'bind': '/data_output_mount_1'},
        os.path.join(cwd, 'pipeline')                       : {'bind': '/pipeline'},
#        os.path.join(cwd, 'docker', 'render-python-apps')   : {'bind': '/shared/render-python-apps'},
#        os.path.join(cwd, 'docker', 'render-modules')       : {'bind': '/shared/render-modules'}
    }

    #docker compose file
    composeFile = os.path.join(cwd, "docker", "init", "docker-compose.yml")

    try:
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
            if startRenderBackend(composeFile) == False:
                raise Exception("Failed starting the RenderBackend")

            #Start the atcore container
            dManager.startContainer("atcore", atCoreMounts)

    except ValueError as e:
        logger.error("ValueError: " + str(e))

    except Exception as e:
        logger.error("Exception: " + str(e))



if __name__ == '__main__':
    main()
