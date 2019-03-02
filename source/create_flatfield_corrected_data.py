import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit
import time
def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    flatfield_output_dir    = os.path.join(p.dataOutputFolder, "flatfield")

    #Make sure output folder exists
    if os.path.isdir(flatfield_output_dir) == False:
       os.mkdir(flatfield_output_dir)

    #stacks
    acq_stack        = "S%d_Session%d"%(session,session)
    median_stack     = "S%d_Medians"%(session)
    flatfield_stack  = "S%d_FlatFielded"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    #Create json files and apply median.
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(p.flatfield_template) as json_data:
             ff = json.load(json_data)

        flatfield_json_file = "flatfield_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, sectnum)

        z = ribbon*100 + sectnum

        u.saveflatfieldjson(ff, os.path.join(flatfield_output_dir, flatfield_json_file), renderProject, acq_stack, median_stack, flatfield_stack, posixpath.join(p.dockerDataOutputFolder, "flatfield"), z, True)
        cmd = "docker exec " + p.atCoreContainer
        cmd = cmd + " python -m rendermodules.intensity_correction.apply_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(posixpath.join(p.dockerDataOutputFolder, "flatfield", flatfield_json_file))

        #Run =============
        print ("Running: " + cmd.replace('--', '\n--'))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout.readlines():
            print (line)
        proc.wait()
        if proc.returncode:
            print ("PROC_RETURN_CODE:" + str(proc.returncode))
            raise Exception(os.path.basename(__file__) + " threw an Exception")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
