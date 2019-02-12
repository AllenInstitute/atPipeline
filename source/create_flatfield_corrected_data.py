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
    flatfield_dir    = os.path.join(projectroot, p.dataOutputFolder, "flatfield")

    #Make sure output folder exists
    if os.path.isdir(flatfield_dir) == False:
       os.mkdir(flatfield_dir)

    #stacks
    acq_stack        = "S%d_Session%d"%(session,session)
    median_stack     = "S%d_Medians"%(session)
    flatfield_stack  = "S%d_FlatFielded"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    #Create json files and apply median.
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(u.flatfield_template) as json_data:
             ff = json.load(json_data)

        flatfield_json = os.path.join(flatfield_dir, "flatfield""_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, sectnum))

        z = ribbon*100 + sectnum

        u.saveflatfieldjson(ff, flatfield_json, renderProject.host, renderProject.owner, renderProject.name, acq_stack, median_stack, flatfield_stack, u.toDockerMountedPath(flatfield_dir, p.prefixPath), z, True)
        cmd = "docker exec " + p.atCoreContainer
        cmd = cmd + " python -m rendermodules.intensity_correction.apply_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(flatfield_json, p.prefixPath))

        #Run =============
        print ("Running: " + cmd.replace('--', '\n--'))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout.readlines():
            print (line)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
