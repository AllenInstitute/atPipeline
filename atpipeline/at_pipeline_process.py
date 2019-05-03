import logging
import subprocess
import os
from abc import ABC, abstractmethod
from . import at_system_config
from . import at_utils as u

logger = logging.getLogger('atPipeline')

class PipelineProcess(ABC):

    def __init__(self, _paras : at_system_config.ATSystemConfig, _name):
        self.paras = _paras
        self.name = _name
        self.sessionFolders = self.createSessionFolders()

        #Setup and create status file
        self.status_files_folder = os.path.join(self.paras.absoluteDataOutputFolder, 'status')

        if not os.path.exists(self.status_files_folder):
            try:
                os.makedirs(self.status_files_folder)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        self.status_file    = os.path.join(self.status_files_folder, self.name + "-status.log")
        if os.path.isfile(self.status_file) == False:
            open(self.status_file, 'a').close()


    def get_name(self):
        return self.name

    def check_if_done(self):
        #Read status file (for now just the first line, True or False)

        with open(self.status_file,'r') as f:
            line = f.readline()
            if len(line) > 3:
                aWord = line.split(None, 1)[0]
                if aWord == 'True':
                    return True

        return False

    #@abstractmethod
    def validate(self):
        #Reimplement this in subclasses
        with open(self.status_file,'w') as f:
            f.truncate()
            f.write('True')
        return True

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

    def submit(self, cmd):
        logger.info(" Submitting job: " + self.name + ". \n\nCMD: " + cmd.replace('--', '\n--') + "\n...........................")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in proc.stdout.readlines():
            logger.debug(line.rstrip())

        proc.wait()
        if proc.returncode:
            logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
            raise Exception("Error in pipeline step: " + self.name)

