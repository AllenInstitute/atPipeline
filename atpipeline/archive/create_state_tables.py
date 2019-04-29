import os
import subprocess
import at_utils as u
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

    logger.info("=========== Creating state tables for session: " + sessionFolder + " ===============")
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    for sectnum in range(p.firstSection, p.lastSection + 1):
        logger.debug("Processing section: " + str(sectnum))

        #State table file
        statetablefile = p.getStateTableFileName(ribbon, session, sectnum)
        logger.info("Creating statetable file: " + statetablefile)

        if os.path.exists(statetablefile):
           logger.info("The statetable: " + statetablefile + " already exists. Continuing..")
        else:
            cmd = "docker exec " + p.systemParameters.atCoreContainer
            cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"        %(u.toDockerMountedPath(projectroot,    p))
            cmd = cmd + " --outputFile %s"              %(u.toDockerMountedPath(statetablefile, p))
            cmd = cmd + " --ribbon %d"                  %ribbon
            cmd = cmd + " --session %d"                 %session
            cmd = cmd + " --section %d"                 %(sectnum)
            cmd = cmd + " --oneribbononly True"

		#Run ====================
            u.runPipelineStep(cmd, "create_state_tables")

if __name__ == "__main__":
    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
