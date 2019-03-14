#The ATPipeline class
import atutils as u
import logging
import os
import at_system_config as c
import docker
import subprocess

logger = logging.getLogger('atPipeline')

class ATPipeline:
    def __init__(self, parameters : c.ATSystemConfig):
        self.parameters = parameters

        dockerClient = docker.from_env()
        atcore = dockerClient.containers.get("atcore")
        render = dockerClient.containers.get("tk_render")

        if render.status != "running":
            raise ValueError("The Render docker container is not running!")

        if atcore.status != "running":
            raise ValueError("The atcore docker container is not running!")

    def run(self):
        logger.info("ATPipeline run")
        pass

class Stitch(ATPipeline):
    def __init__(self, _paras):
        super().__init__(_paras)

        p = self.parameters
        #Define the pipeline
        self.createStateTables              = CreateStateTables(p)
        self.createRawDataRenderStacks      = CreateRawDataRenderStacks(p)
        self.createMedianFiles              = CreateMedianFiles(p)

    def run(self):
        ATPipeline.run(self)
        #Check what pipeline to run
        for ribbon in self.parameters.ribbons:
            sessionFolders = []
            #Create session folders
            for session in self.parameters.sessions:
              sessionFolders.append(os.path.join(self.parameters.projectDataFolder, self.parameters.projectDataFolder, "raw", "data", ribbon, session))

            for sessionFolder in sessionFolders:
                self.createStateTables.run(sessionFolder)
                #self.createRawDataRenderStacks.run(sessionFolder)
                #self.createMedianFiles,run(sessionFolder)

        return True

class PipelineProcess():
    def __init__(self, _paras, _name):
        self.paras = _paras
        self.name = _name

    def run(self, sessionFolder):
        [self.projectroot, self.ribbon, self.session] = u.parse_session_folder(sessionFolder)


    def submit(self, cmd):
        logger.info("===================== Running command: " + cmd.replace('--', '\n--') + "\n---------------------------------------")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in proc.stdout.readlines():
            logger.debug(line.rstrip())

        proc.wait()
        if proc.returncode:
            logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
            raise Exception("Error in pipeline step: " + self.name)

    def validate():
        pass

class CreateStateTables(PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateStateTables")

    def run(self, sessionFolder):
        PipelineProcess.run(self, sessionFolder)
        logger.info("=========== Creating state tables for session: " + sessionFolder + " ===============")

        for sectnum in range(self.paras.firstSection, self.paras.lastSection + 1):
            logger.debug("Processing section: " + str(sectnum))

            #State table file
            statetablefile = self.paras.getStateTableFileName(self.ribbon, self.session, sectnum)
            logger.info("Creating statetable file: " + statetablefile)

            if os.path.exists(statetablefile) and self.paras.overwritedata == False:
               logger.info("The statetable: " + statetablefile + " already exists. Continuing..")
            else:
                cmd = "docker exec " + self.paras.atCoreContainer
                cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
                cmd = cmd + " --projectDirectory %s"        %(c.toDockerMountedPath2(self.projectroot,    self.paras))
                cmd = cmd + " --outputFile %s"              %(c.toDockerMountedPath2(statetablefile, self.paras))
                cmd = cmd + " --ribbon %d"                  %(self.ribbon)
                cmd = cmd + " --session %d"                 %(self.session)
                cmd = cmd + " --section %d"                 %(sectnum)
                cmd = cmd + " --oneribbononly True"

    		  #Run ====================
                self.submit(cmd)


class CreateRawDataRenderStacks(PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateRawDataRenderStacks")

    def run(self, sessionFolder):

        p = self.paras
        logger.info("Processing session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        rp     = p.renderProject

        for sectnum in range(p.firstSection, p.lastSection + 1):
            logger.info("Processing section: " + str(sectnum))

            #State table file
            statetablefile = p.getStateTableFileName(ribbon, session, sectnum)

            #upload acquisition stacks
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python -m renderapps.dataimport.create_fast_stacks_multi"
            cmd = cmd + " --render.host %s"           %rp.host
            cmd = cmd + " --render.owner %s "         %rp.owner
            cmd = cmd + " --render.project %s"        %rp.projectName
            cmd = cmd + " --render.client_scripts %s" %rp.clientScripts
            cmd = cmd + " --render.port %d"           %rp.hostPort
            cmd = cmd + " --render.memGB %s"          %rp.memGB
            cmd = cmd + " --log_level %s"             %rp.logLevel
            cmd = cmd + " --statetableFile %s"        %(c.toDockerMountedPath2(statetablefile,  p))
            cmd = cmd + " --projectDirectory %s"      %(c.toDockerMountedPath2(projectroot,   p))
            cmd = cmd + " --dataOutputFolder %s"      %(p.dataOutputFolder.replace('\\', '/'))
            cmd = cmd + " --outputStackPrefix S%d_"   %(session)
            cmd = cmd + " --reference_channel %s"      %(p.referenceChannelRegistration)

    	  #Run =============
            u.runPipelineStep(cmd, __file__)

##class CreateR(PipelineProcess):
##
##    def __init__(self, _paras):
##        super().__init__(_paras)
##
##    def run(self, sessionFolder):

class CreateMedianFiles(PipelineProcess):

    def __init__(self, _paras):
        super().__init__(_paras, "CreateMedianFiles")

    def run(self, sessionFolder):
        logger.info("Processing session folder: " + sessionFolder)
        [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

        #Output directories
        median_dir       = os.path.join("%s"%projectroot, p.dataOutputFolder, "medians")
        median_json      = os.path.join(median_dir, "median_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

        #Make sure output folder exist
        if os.path.isdir(median_dir) == False:
            os.mkdir(median_dir)

        #stacks
        acq_stack        = "S%d_Session%d"%(session, session)
        median_stack     = "S%d_Medians"%(session)

        rp               = p.renderProject

        with open(p.systemParameters.median_template) as json_data:
            med = json.load(json_data)

        u.savemedianjson(med, median_json, rp, acq_stack, median_stack, u.toDockerMountedPath(median_dir, p), ribbon*100 + p.firstSection, ribbon*100 + p.lastSection, True)

        cmd = "docker exec " + p.sys.atCoreContainer
        cmd = cmd + " python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(median_json,  p))

        #Run =============
        u.runPipelineStep(cmd, __file__)

