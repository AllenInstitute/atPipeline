import os
import json
import sys
import subprocess
import posixpath
import at_utils as u
import timeit
import time
import logging

logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

    logger.info("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject     = u.RenderProject("ATExplorer", p.renderHost, p.projectName)

    #RUN python script to calculate scale and background factors for each channel.
    cmd = "python deconv_scale_factor_session.py"
    cmd = cmd + "  --drive %s"%(u.toDockerMountedPath(projectroot, p))
    cmd = cmd + " --project %s"%renderProject.projectName
    cmd = cmd + " --ribbon %s"%ribbon
    cmd = cmd + " --session %s"%session
    cmd = cmd + " --section %s"%p.firstSection

    #Run =============
    u.runPipelineStep(cmd, __file__)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
