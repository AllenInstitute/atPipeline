#The ATPipeline class
import atutils as u
import logging
import os
import at_system_config as c
import docker

logger = logging.getLogger('atPipeline')

class ATPipeline:
    def __init__(self, parameters : c.ATSystemConfig):
        self.fineAlign = None
        #self.prepareFoqrRegistration
        self.parameters = parameters
        #self.createStateTables

        dockerClient = docker.from_env()
        atcore = dockerClient.containers.get("atcore")
        render = dockerClient.containers.get("tk_render")

        if render.status != "running":
            raise ValueError("The Render docker container is not running!")

        if atcore.status != "running":
            raise ValueError("The atcore docker container is not running!")



    def run(self):
        #Check what pipeline to run
        if self.parameters.pipeline == "stitch":
            logger.info("Running stitching pipeline")
        self.stitch()

    def stitch(self):
        self.createStateTables = CreateStateTables(self.parameters)
        for ribbon in self.parameters.ribbons:

            sessionFolders = []
            #Create session folders
            for session in self.parameters.sessions:
              sessionFolders.append(os.path.join(self.parameters.projectDataFolder, "raw", "data", ribbon, session))

            for sessionFolder in sessionFolders:
                self.createStateTables.run(os.path.join(self.parameters.projectDataFolder, sessionFolder))


class PipelineProcess():
    def __init__(self, _paras):
        self.paras = _paras

    def run(self, sessionFolder):
        pass

class CreateStateTables(PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras)

    def run(self, sessionFolder):
        logger.info("=========== Creating state tables for session: " + sessionFolder + " ===============")
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        for sectnum in range(self.paras.firstSection, self.paras.lastSection + 1):
            logger.debug("Processing section: " + str(sectnum))

            #State table file
            statetablefile = self.paras.getStateTableFileName(ribbon, session, sectnum)
            logger.info("Creating statetable file: " + statetablefile)

            if os.path.exists(statetablefile):
               logger.info("The statetable: " + statetablefile + " already exists. Continuing..")
            else:
                cmd = "docker exec " + self.paras.atCoreContainer
                cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
                cmd = cmd + " --projectDirectory %s"        %(c.toDockerMountedPath2(projectroot,    self.paras))
                cmd = cmd + " --outputFile %s"              %(c.toDockerMountedPath2(statetablefile, self.paras))
                cmd = cmd + " --ribbon %d"                  %ribbon
                cmd = cmd + " --session %d"                 %session
                cmd = cmd + " --section %d"                 %(sectnum)
                cmd = cmd + " --oneribbononly True"

    		  #Run ====================
                u.runPipelineStep(cmd, "create_state_tables")


