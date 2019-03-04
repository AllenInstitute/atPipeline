import os
import subprocess
import posixpath
import atutils as u
import timeit
import json

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    dataOutputFolder        = os.path.join(p.dataOutputFolder,          "rough_aligned")
    docker_dataOutputFolder = posixpath.join(p.dockerDataOutputFolder,  "rough_aligned")

    input_json_file         = "roughalignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection)
    output_json_file        = "output_roughalignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection)

    #stacks
    inputStack     = "S%d_Stitched_Dropped_LowRes"%(session)
    outputStack    = "S%d_RoughAligned_LowRes"%(session)

    renderProject  = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName, p.renderHostPort, p.clientScripts)

	#point match collections
    lowresPmCollection = "%s_lowres_round"%renderProject.name

    with open(p.alignment_template) as json_data:
       ra = json.load(json_data)

    #Create folder if not exists
    if os.path.isdir(dataOutputFolder) == False:
        os.mkdir(dataOutputFolder)

    u.saveRoughAlignJSON(ra, os.path.join(dataOutputFolder, input_json_file), renderProject, inputStack, outputStack, lowresPmCollection, p.logLevel, p.firstSection, p.lastSection, docker_dataOutputFolder)

    #Run docker command
    cmd = "docker exec " + p.atCoreContainer
    cmd = cmd + " python -m rendermodules.solver.solve"
    cmd = cmd + " --input_json %s" %(posixpath.join(docker_dataOutputFolder, input_json_file))
    cmd = cmd + " --output_json %s"%(posixpath.join(docker_dataOutputFolder, output_json_file))

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("Error creating rough aligned stacks")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
