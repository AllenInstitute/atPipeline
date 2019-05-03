import os
import json
import sys
import subprocess
import posixpath
import at_utils as u
import timeit
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

    logger.info("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    rp     = p.renderProject

    for sectnum in range(p.firstSection, p.lastSection + 1):
        logger.info("Processing section: " + str(sectnum))

        #State table file
        statetablefile = p.getStateTableFileName(ribbon, session, sectnum)

        #upload acquisition stacks
        cmd = "docker exec " + p.sys.atCoreContainer
        cmd = cmd + " python -m renderapps.dataimport.create_fast_stacks_multi"
        cmd = cmd + " --render.host %s"           %rp.host
        cmd = cmd + " --render.owner %s "         %rp.owner
        cmd = cmd + " --render.project %s"        %rp.projectName
        cmd = cmd + " --render.client_scripts %s" %rp.clientScripts
        cmd = cmd + " --render.port %d"           %rp.hostPort
        cmd = cmd + " --render.memGB %s"          %rp.memGB
        cmd = cmd + " --log_level %s"             %rp.logLevel
        cmd = cmd + " --statetableFile %s"        %(u.toDockerMountedPath(statetablefile,  p))
        cmd = cmd + " --projectDirectory %s"      %(u.toDockerMountedPath(projectroot,   p))
        cmd = cmd + " --dataOutputFolder %s"      %(p.dataOutputFolder.replace('\\', '/'))
        cmd = cmd + " --outputStackPrefix S%d_"   %(session)
        cmd = cmd + " --reference_channel %s"      %(p.referenceChannel)

	  #Run =============
        u.runPipelineStep(cmd, __file__)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
