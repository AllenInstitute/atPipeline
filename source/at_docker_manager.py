import docker
import logging
#A simple docker manager, wrapping some of the DockerSDK1

class DockerManager:
    def __init__(self):
        self.dClient = docker.from_env()
        logger = logging.getLogger('atPipeline')

    def startContainer(self, ctrName, mounts : 'Dictionary of mounts'):

        if self.removeContainer(ctrName) == True:
            logger.info("Removed atcore container")

        #This will do nothing, forever
        cmd = "tail -f /dev/null"
        ctr = self.dClient.containers.run('atpipeline/atcore', command=cmd, volumes= mounts, name=ctrName, detach=True)

        if ctr == None:
           return False

        if ctr.status == "running" or ctr.status == "created":
            return True
        return False

    def getContainer(self, ctrName):
        containers = self.dClient.containers.list(all=True)
        for ctr in containers:
            if ctr.name == ctrName:
                return ctr
        return None

    def stopContainer(self, ctrName):
        ctr = self.getContainer(ctrName)
        if ctr != None:
            ctr.kill()
            return True

        return False

    def killAllContainers(self):

        containers = self.dClient.containers.list(all=True)
        for ctr in containers:
            if ctr.status == 'running':
                ctr.kill()

        return True

    def removeContainer(self, ctrName):
        ctr = self.getContainer(ctrName)
        if ctr != None:
            ctr.remove()
            return True

        return False
