import docker
import logging
import os
import subprocess
import pathlib
from . import at_system_config
import argparse
logger = logging.getLogger('atPipeline')

#A simple docker manager, wrapping some of the DockerSDK
class DockerManager:
    def __init__(self, configFolder=None, atcore_image_tag=None, cmdFlags=[]):

        logger = logging.getLogger('atPipeline')
        self.argparser = argparse.ArgumentParser('backend_management')
        self.dClient = docker.from_env()

        self.atCoreMounts = {}
        self.composeFile = ""

        if configFolder:
            self.configFolder = configFolder
        elif 'AT_SYSTEM_CONFIG_FOLDER' in os.environ:
            self.configFolder = os.environ['AT_SYSTEM_CONFIG_FOLDER']
        elif os.name == 'posix':
            self.configFolder = '/usr/local/etc/'
        else:
            raise Exception("No default configFolder folder defined for %s. Set environment variable 'AT_SYSTEM_CONFIG_FOLDER' to the folder where the file 'at-system-config.ini' exists." % os.name)

        self.paras = at_system_config.ATSystemConfig(os.path.join(self.configFolder, 'at-system-config.ini'),
            cmdFlags=cmdFlags)

        self.paras.createReferences(caller="backend_management")
        self.setComposeFile(os.path.join(self.configFolder, 'at-docker-compose.yml'))
        self.setupMounts()

        if atcore_image_tag:
            self.atcore_image_tag = atcore_image_tag
        else:
            self.atcore_image_tag = self.paras.GENERAL['AT_CORE_DOCKER_IMAGE_TAG']

    def prune_containers(self):
        val = self.dClient.containers.prune()
        logger.info(val)

    def prune_images(self):
        val = self.dClient.images.prune()
        logger.info(val)

    def prune_all(self):
        self.prune_containers()
        self.prune_images()

    def status(self):
        containers = self.dClient.containers.list(all=True)

        for ctr in containers:
            logger.info("Container: " + ctr.name + " : " + ctr.status)

        #If everythin is ok, return 0
        return 0

    def setComposeFile(self, fName):
        #Check that file exists, otherwise raise an error
        if os.path.isfile(fName) == False:
            raise Exception("The docker compose file: " + fName + " don't exist.")

        self.composeFile = fName

    def setupMounts(self, mountRenderPythonApps = False, mountRenderModules = False):
        logger.debug("Setting up container mounts.")

        mountCount = 1
        for mount in self.paras.mounts:
            mountValue  = {'bind' : mount[1] , 'mode' : 'rw'}
            self.atCoreMounts[mount[0]] = mountValue
            mountCount = mountCount + 1

        #if mountRenderPythonApps == True:
        #    self.atCoreMounts[os.path.join(cwd, 'docker', 'render-python-apps')] = {'bind': '/shared/render-python-apps'}

        #if mountRenderModules == True:
        #    self.atCoreMounts[os.path.join(cwd, 'docker', 'render-modules')] = {'bind': '/shared/render-modules'}

        #Mount pipeline
        #self.atCoreMounts['/local2/atpipeline/pipeline'] = {'bind' : '/pipeline', 'mode' : 'ro'}

    def reStartContainer(self, ctrName):
        logger.info("Restarting the container: " + ctrName)
        self.stopContainer(ctrName)
        return self.startContainer(ctrName)

    def startContainer(self, ctrName):
        try:
            ctrCheck = self.dClient.containers.get(ctrName)
            if ctrCheck.status == 'running':
                logger.warning("The container: " + ctrName + " is already running")
                return False

            if self.removeContainer(ctrName) == True:
                logger.info("Removed " + ctrName + " container")
        except docker.errors.NotFound:
            pass

        if ctrName == "atcore":
            #This will do nothing, forever
            cmd = "tail -f /dev/null"
            ctr = self.dClient.containers.run("atpipeline/atcore:" + self.atcore_image_tag, volumes=self.atCoreMounts, command=cmd, cap_add=["SYS_ADMIN"], privileged=True, name=ctrName, detach=True)


            if ctr == None:
               return False

            if ctr.status != "running" and ctr.status != "created":
                #Failing starting a container is considered a showstopper. Raise an exception
                raise Exception("Failed starting container: " + ctrName)
            logger.info("Started the " + ctrName + " container using image tag: " + self.atcore_image_tag)

        else:
                raise Exception("The ATBackend don't manage the container: \"" + ctrName + "\"")


        return True

    def getContainer(self, ctrName):
        containers = self.dClient.containers.list(all=True)
        for ctr in containers:
            if ctr.name == ctrName:
                return ctr
        return None

    def stopContainer(self, ctrName):
        ctr = self.getContainer(ctrName)

        if ctr == None:
            logger.info("The container: " + ctrName + " does not exist")
            return False

        if ctr and ctr.status != 'running':
            logger.info("The container: " + ctrName + " is not running")
            return False

        ctr.kill()
        return True

    def killAllContainers(self):
        containers = self.dClient.containers.list(all=True)
        for ctr in containers:
            if ctr.status == 'running':
                logger.info("Killing container: " + ctr.name)
                ctr.kill()

        return True

    def reStartAll(self):
        self.killAllContainers()
        self.startContainer('atcore')
        self.startRenderBackend()

    def startAll(self):
        self.startContainer('atcore')
        self.startRenderBackend()

    def removeContainer(self, ctrName):
        ctr = self.getContainer(ctrName)
        if ctr != None:
            ctr.remove()
            return True

        return False

    def startRenderBackend(self):

        cmd = "docker-compose -p default -f " + str(self.composeFile)
        cmd = cmd + " up -d "
        logger.info("Running: " + cmd)

        #Output here looks ugly !!
        if os.name =='posix':
            useShell = True
        else:
            useShell = False

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=useShell, stderr=subprocess.STDOUT, encoding='ascii')
        for line in proc.stdout.readlines():
            logger.info(line.rstrip())

        print ("\n ---- running containers follows -----\n")
        cmd = "docker ps"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=useShell, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in p.stdout.readlines():
            print (line.rstrip())

        return True
