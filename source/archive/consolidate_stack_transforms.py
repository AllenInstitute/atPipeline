##Create new
import os
import json
import sys
import subprocess
import posixpath
import at_utils as u
import timeit
import logging

logger = logging.getLogger('atPipeline')

##Create a new stack with "consolidated" transforms
def run(p : u.ATDataIni, sessionFolder):
    logger.info("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    rp = p.renderProject

    cmd = "docker exec "+ p.sys.atCoreContainer
    cmd = cmd + " python -m rendermodules.stack.consolidate_transforms"
    cmd = cmd + " --render.host %s"                             %(rp.host)
    cmd = cmd + " --render.project %s"                          %(rp.projectName)
    cmd = cmd + " --render.owner %s"                            %(rp.owner)
    cmd = cmd + " --render.client_scripts %s"                   %(rp.clientScripts)
    cmd = cmd + " --render.memGB %s"                            %(rp.memGB)
    cmd = cmd + " --render.port %s"                             %(rp.hostPort)
    cmd = cmd + " --pool_size %s"                               %(p.sys.atCoreThreads)
    cmd = cmd + " --stack S%d_RoughAligned"                     %(session)
    cmd = cmd + " --output_stack S%d_RoughAligned_Consolidated" %(session)
    cmd = cmd + " --close_stack %d"                             %(True)
    cmd = cmd + " --output_json Test"

    # Run =============
    logger.info("Running: " + cmd.replace('--', '\n--'))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    for line in proc.stdout.readlines():
    	logger.info(line.rstrip())

    proc.wait()
    if proc.returncode:
        logger.info("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("consolidate_stack_transforms threw an Exception")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)


