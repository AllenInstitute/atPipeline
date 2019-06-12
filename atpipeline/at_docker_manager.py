import docker
import logging
import os
import subprocess
import pathlib
import argparse
from atpipeline import at_system_config
from atpipeline import at_backend_arguments
logger = logging.getLogger('atPipeline')

#A simple docker manager, wrapping some of the DockerSDK
class DockerManager:
    def __init__(self, system_paras : at_system_config.ATSystemConfig):

        self.paras = system_paras
        self.dClient = docker.from_env()
        self.mounts = {}
        self.composeFile = ""
        self.setComposeFile(os.path.join(self.paras.args.configfolder, 'at-docker-compose.yml'))
        self.setupMounts()
        self.atcoreimagetag = self.paras.args.atcoreimagetag
        self.container_prefix = self.paras.config['GENERAL']['DOCKER_CONTAINER_PREFIX']

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
            if ctr.name.find(self.container_prefix) == 0:
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
            self.mounts[mount[0]] = mountValue
            mountCount = mountCount + 1

        #if mountRenderPythonApps == True:
        #    self.mounts[os.path.join(cwd, 'docker', 'render-python-apps')] = {'bind': '/shared/render-python-apps'}

        #if mountRenderModules == True:
        #    self.mounts[os.path.join(cwd, 'docker', 'render-modules')] = {'bind': '/shared/render-modules'}

        #Mount pipeline
        #self.mounts['/local2/atpipeline/pipeline'] = {'bind' : '/pipeline', 'mode' : 'ro'}

    def reStartContainer(self, ctrName):
        logger.info("Restarting the container: " + ctrName)
        self.stopContainer(ctrName)
        return self.startContainer(ctrName)

    def startContainer(self, ctrName):

        ctrName = self.container_prefix + '_' + ctrName
        try:
            ctrCheck = self.dClient.containers.get(ctrName)
            if ctrCheck.status == 'running':
                logger.warning("The container: " + ctrName + " is already running")
                return False

            if self.removeContainer(ctrName) == True:
                logger.info("Removed " + ctrName + " container")
        except docker.errors.NotFound:
            pass

        if ctrName == self.paras.atcore_ctr_name:
            #This will do nothing, forever
            cmd = "tail -f /dev/null"

            #ctr = self.dClient.containers.run("atpipeline/atcore:" + self.atcore_image_tag, user=17632, volumes=self.mounts, command=cmd, name=ctrName, detach=True)
            ctr = self.dClient.containers.run("atpipeline/atcore:" + self.atcoreimagetag, volumes=self.mounts, command=cmd, name=ctrName, detach=True)

            if ctr == None:
               return False

            if ctr.status != "running" and ctr.status != "created":
                #Failing starting a container is considered a showstopper. Raise an exception
                raise Exception("Failed starting container: " + ctrName)
            logger.info("Started the " + ctrName + " container using image tag: " + self.atcoreimagetag)

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

    #Kill all containers with prefix
    def killAllContainers(self, prefix):
        containers = self.dClient.containers.list(all=True)
        for ctr in containers:
            if ctr.status == 'running':
                if ctr.name.startswith(prefix):
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
        cmd = "docker-compose -p " + self.container_prefix + " -f " + str(self.composeFile)
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
