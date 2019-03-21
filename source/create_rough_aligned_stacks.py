import os
import subprocess
import posixpath
import atutils as u
import timeit
import json
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

    logger.info("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    dataOutputFolder    = os.path.join(projectRoot, p.dataOutputFolder, "rough_aligned")
    input_json          = os.path.join(dataOutputFolder, "roughalignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))
    output_json         = os.path.join(dataOutputFolder, "output_roughalignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

    #stacks
    inputStack     = "S%d_LowRes"%(session)
    outputStack    = "S%d_RoughAligned_LowRes"%(session)

    rp  = p.renderProject

	#point match collections
    lowresPmCollection = "%s_lowres_round"%rp.projectName

    with open(p.systemParameters.alignment_template) as json_data:
       ra = json.load(json_data)

    #Create folder if not exists
    if os.path.isdir(dataOutputFolder) == False:
        os.mkdir(dataOutputFolder)

    u.saveRoughAlignJSON(ra, input_json, rp, inputStack, outputStack, lowresPmCollection, p.firstSection, p.lastSection, u.toDockerMountedPath(dataOutputFolder, p))

    #Run docker command
    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " python -m rendermodules.solver.solve"
    cmd = cmd + " --input_json %s" %(u.toDockerMountedPath(input_json, p))
    cmd = cmd + " --output_json %s"%(u.toDockerMountedPath(output_json, p))

    #Run =============
    u.runPipelineStep(cmd, __file__)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
