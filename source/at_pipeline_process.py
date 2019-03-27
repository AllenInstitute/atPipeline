import at_utils as u
import logging
import subprocess

logger = logging.getLogger('atPipeline')

class PipelineProcess():
    def __init__(self, _paras, _name):
        self.paras = _paras
        self.name = _name

    def run(self, sessionFolder):
        [self.projectroot, self.ribbon, self.session] = u.parse_session_folder(sessionFolder)

    def submit(self, cmd):
        logger.info("\n===================== Running Pipeline Process: " + self.name + ". \n\nCMD: " + cmd.replace('--', '\n--') + "\n---------------------------------------")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in proc.stdout.readlines():
            logger.debug(line.rstrip())

        proc.wait()
        if proc.returncode:
            logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
            raise Exception("Error in pipeline step: " + self.name)

    def validate():
        pass
