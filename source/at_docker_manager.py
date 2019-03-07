import docker
import logging
import os
import subprocess
import pathlib

logger = logging.getLogger('atPipeline')
#A simple docker manager, wrapping some of the DockerSDK

class DockerManager:
    def __init__(self):
        self.dClient = docker.from_env()
        logger = logging.getLogger('atPipeline')
        self.atCoreMounts = {}
        self.composeFile = ""

    def setComposeFile(self, fName):
        #Check that file exists, otherwise raise an error
        if os.path.isfile(fName) == False:
            raise Exception("The docker compose file: " + fName + " don't exist.")

        self.composeFile = fName

    def setupMounts(self, mounts, mountRenderPythonApps = False, mountRenderModules = False):
        cwd = pathlib.Path().absolute().resolve()
        mountCount = 1
        for mount in mounts:
            mountValue  = {'bind' : '/data_mount_' + str(mountCount) , 'mode' : 'rw'}
            self.atCoreMounts[mount] = mountValue
            mountCount = mountCount + 1

        if mountRenderPythonApps == True:
            self.atCoreMounts[os.path.join(cwd, 'docker', 'render-python-apps')] = {'bind': '/shared/render-python-apps'}

        if mountRenderModules == True:
            self.atCoreMounts[os.path.join(cwd, 'docker', 'render-modules')] = {'bind': '/shared/render-modules'}

        #Mount pipeline
        self.atCoreMounts[os.path.join(cwd, 'pipeline')] = {'bind' : '/pipeline', 'mode' : 'ro'}

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
            ctr = self.dClient.containers.run('atpipeline/atcore:dev', volumes=self.atCoreMounts, command=cmd, cap_add=["SYS_ADMIN"], privileged=True, name=ctrName, detach=True)

            if ctr == None:
               return False

            if ctr.status != "running" and ctr.status != "created":
                #Failing starting a container is considered a showstopper. Raise an exception
                raise Exception("Failed starting container: " + ctrName)
        else:
                raise Exception("The ATBackend don't manage the container: \"" + ctrName + "\"")

        logger.info("Started the " + ctrName + " container")
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

        cmd = "docker-compose --no-ansi -f " + str(self.composeFile)
        cmd = cmd + " up -d"
        print ("Running: " + cmd)

        #Output here looks ugly !!
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='ascii')
        for line in proc.stdout.readlines():
            print (line.rstrip())

        print ("\n ---- running containers follows -----\n")
        cmd = "docker ps"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in p.stdout.readlines():
            print (line.rstrip())

        return True
