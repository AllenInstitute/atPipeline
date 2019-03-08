import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

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

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)

