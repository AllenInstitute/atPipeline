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

    #Output directories
    stitching_dir    = os.path.join(projectroot, p.dataOutputFolder, "stitching")

    #Make sure output folder exist
    if os.path.isdir(stitching_dir) == False:
       os.mkdir(stitching_dir)

    #stacks
    flatfield_stack  = "S%d_FlatFielded"%(session)
    stitched_stack   = "S%d_Stitched"%(session)

    renderProject     = p.renderProject

	#Create json files and start stitching...
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(p.systemParameters.stitching_template) as json_data:
             stitching_template = json.load(json_data)

        stitching_json = os.path.join(stitching_dir, "flatfield""_%s_%s_%d.json"%(ribbon, session, sectnum))
        z = ribbon*100 + sectnum

        u.savestitchingjson(stitching_template, stitching_json, renderProject, flatfield_stack, stitched_stack, z)

        cmd = "docker exec " + p.sys.atCoreContainer
        cmd = cmd + " java -cp /shared/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC"
        cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(stitching_json, p))

        #Run =============
        u.runPipelineStep(cmd, "create_state_tables")

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)


