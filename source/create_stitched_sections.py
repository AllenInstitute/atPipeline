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
    stitching_dir    = os.path.join(projectroot, p.dataOutputFolder, "stitching")

    #Make sure output folder exist
    if os.path.isdir(stitching_dir) == False:
       os.mkdir(stitching_dir)

    #stacks
    flatfield_stack  = "S%d_FlatFielded"%(session)
    stitched_stack   = "S%d_Stitched"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

	#Create json files and start stitching...
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(p.stitching_template) as json_data:
             stitching_template = json.load(json_data)

        stitching_json = os.path.join(stitching_dir, "flatfield""_%s_%s_%d.json"%(ribbon, session, sectnum))
        z = ribbon*100 + sectnum

        u.savestitchingjson(stitching_template, stitching_json, renderProject, flatfield_stack, stitched_stack, z)

        cmd = "docker exec " + p.atCoreContainer
        cmd = cmd + " java -cp /shared/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC"
        cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(stitching_json, p.prefixPath))

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


