import docker
import logging
import os
import subprocess

logger = logging.getLogger('atPipeline')
#A simple docker manager, wrapping some of the DockerSDK

class DockerManager:
    def __init__(self):
        self.dClient = docker.from_env()
        logger = logging.getLogger('atPipeline')

    def reStartContainer(self, ctrName, mounts):
        logger.info("Restarting the container: " + ctrName )
        self.stopContainer(ctrName)
        return self.startContainer(ctrName, mounts)

    def startContainer(self, ctrName, mounts : 'Dictionary of mounts'):

        try:
            ctrCheck = self.dClient.containers.get(ctrName)
            if ctrCheck.status == 'running':
                logger.warning("The container: " + ctrName + " is already running")
                return False

            if self.removeContainer(ctrName) == True:
                logger.info("Removed " + ctrName + " container")
        except docker.errors.NotFound:
            pass

        #This will do nothing, forever
        cmd = "tail -f /dev/null"
        ctr = self.dClient.containers.run('atpipeline/atcore:dev', volumes=mounts, command=cmd, cap_add=["SYS_ADMIN"], privileged=True, name=ctrName, detach=True)

        if ctr == None:
           return False

        if ctr.status != "running" and ctr.status != "created":
            #Failing starting a container is considered a showstopper. Raise an exception
            raise Exception("Failed starting container: " + ctrName)

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

    def removeContainer(self, ctrName):
        ctr = self.getContainer(ctrName)
        if ctr != None:
            ctr.remove()
            return True

        return False

    def startRenderBackend(self, composeFile):

        if os.path.exists(composeFile) == False:
            raise Exception("The docker compose file: " + composeFile + " don't exist!")

        cmd = "docker-compose -f " + str(composeFile)
        cmd = cmd + " up -d"
        print ("Running: " + cmd.replace('--', '\n--'))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in proc.stdout.readlines():
            print (line)

        cmd = "docker ps"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in p.stdout.readlines():
            print (line)

        return True
