import os
import sys
import logging
import timeit
import pathlib
import docker
import argparse
from source import *
import source.atutils as u

def main():
    logger = logging.getLogger("atPipeline")
    logger.setLevel(logging.DEBUG)

    try:
        #Get processing parameters
        parser = argparse.ArgumentParser()
        parser.add_argument('-startAll', help='Start the AT backend')
        parser.add_argument('-stopAll', help='Stop the AT backend')

        parser.add_argument("--start", help="Start a specific backend container, e.g. atcore")
        args = parser.parse_args()

        mounts={'/c/data':{'bind': '/mnt/'}}
        dClient = docker.from_env()
        atcore = dClient.containers.get("atcore")
        render = dClient.containers.get("init_render_1")
        if args.start:
            if args.start == "atcore":
                output = dClient.containers.run('atpipeline/atcore', 'echo "hello"', volumes=mounts, detach=True)

        print (output.logs())
##
##        if render.status != "running":
##            raise ValueError("The Render docker container is not running!")
##
##        if atcore.status != "running":
##            raise ValueError("The atcore docker container is not running!")


    except ValueError as error:
        print ("A value error occured: " + str(error))
    except :
        print ("An error occured..")
        e = sys.exc_info()[0]
        print (e)


if __name__ == '__main__':
    main()
