import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    median_dir         = os.path.join(p.dataOutputFolder, "medians")
    docker_median_dir  = posixpath.join(p.dockerDataOutputFolder, "medians")

    median_json_file   = "median_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection)

    #Make sure output folder exist
    if os.path.isdir(median_dir) == False:
       os.mkdir(median_dir)

    #stacks
    acq_stack        = "S%d_Session%d"%(session, session)
    median_stack     = "S%d_Medians"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    with open(p.median_template) as json_data:
         med = json.load(json_data)

    u.savemedianjson(med, os.path.join(median_dir, median_json_file), renderProject, acq_stack, median_stack, docker_median_dir, ribbon*100 + p.firstSection, ribbon*100 + p.lastSection, True)

    cmd = "docker exec " + p.atCoreContainer
    cmd = cmd + " python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
    cmd = cmd + " --render.port 80"
    cmd = cmd + " --input_json %s"%(posixpath.join(docker_median_dir, median_json_file))

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("Error generating median files")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)

