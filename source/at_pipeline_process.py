import at_utils as u
import logging
import subprocess
import at_system_config
import os
from abc import ABC, abstractmethod

logger = logging.getLogger('atPipeline')

class PipelineProcess():
    def __init__(self, _paras : at_system_config.ATSystemConfig, _name):
        self.paras = _paras
        self.name = _name
        self.sessionFolders = self.createSessionFolders()

    @abstractmethod
    def checkIfDone(self):
        pass

    def createSessionFolders(self):
        p = self.paras
        sessionFolders = []
        for ribbon in p.ribbons:
            #Create session folders
            for session in p.sessions:
              sessionFolders.append(os.path.join(p.projectDataFolder, "raw", "data", ribbon, session))

        return sessionFolders

    def run(self):
        logger.info(" Running Pipeline Process: " + self.name + " =======================")
        self.checkIfDone()

    def submit(self, cmd):
        logger.info(" Submitting job: " + self.name + ". \n\nCMD: " + cmd.replace('--', '\n--') + "\n...........................")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in proc.stdout.readlines():
            logger.debug(line.rstrip())

        proc.wait()
        if proc.returncode:
            logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
            raise Exception("Error in pipeline step: " + self.name)

    def validate(self):
        logger.info(" ===================== Validating Process: " + self.name + " =======================")
        return 0
