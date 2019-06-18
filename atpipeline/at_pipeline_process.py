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
        for line in proc.stdout:
            logger.debug(line.rstrip())

        proc.wait()
        if proc.returncode:
            logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
            raise Exception("Error in pipeline step: " + self.name)

        return True

    def submit_atcore(self, cmd, container_name=None, use_container=True):
        """Submit a command to be run in the atcore container.
        Parameters
        ==========
        cmd: str
            Command to be run.
        container_name: str or None
            Name of container to use (or p.atcore_ctr_name if None)
        use_container: bool
            Use the atcore container (true) or execute directly (false).
            Set to false if already running inside the atcore container.
        """
        p = self.paras
        if use_container:
            if container_name is None:
                container_name = p.atcore_ctr_name
            if p.atcore_user_flag:
                userflag = "--user %d:%d" % (p.atcore_uid, p.atcore_gid)
                newcmd = "docker exec %s %s %s" % (userflag, container_name, cmd)
            else:
                newcmd = "docker exec %s %s" % (container_name, cmd)
            return self.submit(newcmd)
        else:
            # This call is being made inside the container. Don't add 'docker exec'.
            return self.submit(cmd)
