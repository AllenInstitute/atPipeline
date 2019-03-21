import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit
import time
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

    logger.info("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    flatfield_dir    = os.path.join(projectroot, p.dataOutputFolder, "flatfield")

    #Make sure output folder exists
    if os.path.isdir(flatfield_dir) == False:
       os.mkdir(flatfield_dir)

    #stacks
    acq_stack        = "S%d_Session%d"%(session,session)
    median_stack     = "S%d_Medians"%(session)
    flatfield_stack  = "S%d_FlatFielded"%(session)

    renderProject     = p.renderProject

    #Create json files and apply median.
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(p.systemParameters.flatfield_template) as json_data:
             ff = json.load(json_data)

        flatfield_json = os.path.join(flatfield_dir, "flatfield_%s_%s_%s_%d.json"%(renderProject.projectName, ribbon, session, sectnum))

        z = ribbon*100 + sectnum

        u.saveflatfieldjson(ff, flatfield_json, renderProject, acq_stack, median_stack, flatfield_stack, u.toDockerMountedPath(flatfield_dir, p), z, True)
        cmd = "docker exec " + p.sys.atCoreContainer
        cmd = cmd + " python -m rendermodules.intensity_correction.apply_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(flatfield_json, p))

        #Run =============
        u.runPipelineStep(cmd, __file__)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
