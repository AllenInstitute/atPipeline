import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit
import time

def run(firstsection, lastsection, sessionFolder, renderProject, prefixPath):

    [dataRootFolder, ribbon, session] = atutils.parse_session_folder(sessionFolder)

    #Output directories
    stitching_dir    = os.path.join("%s"%dataRootFolder, "processed", "stitching")

    #Make sure output folder exist
    if os.path.isdir(stitching_dir) == False:
       os.mkdir(stitching_dir)

    #stacks
    acq_stack        = "ACQ_Session%d"%(session)
    median_stack     = "MED_Session%d"%(session)
    flatfield_stack  = "FF_Session%d"%(session)
    stitched_stack   = "STI_FF_Session%d"%(session)

	#Create json files and start stitching...
    for sectnum in range(firstsection -1, lastsection):
        z = ribbon*100 + sectnum

        with open(atutils.stitchingtemplate) as json_data:
             stitching_template = json.load(json_data)

        stitching_json    = os.path.join(stitching_dir, "flatfield""_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, sectnum))
        atutils.savestitchingjson(stitching_template, stitching_json, renderProject.owner, renderProject.name, flatfield_stack, stitched_stack, z)


        cmd = "docker exec atmodules java -cp ./target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC"
        cmd = cmd + " --input_json %s"%(atutils.toDockerMountedPath(stitching_json, prefixPath))

        #Run =============
        print ("Running: " + cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print (line)

if __name__ == "__main__":

    timeStart = timeit.default_timer()

    firstsection = 1
    lastsection = 2

    render_host     = "W10DTMJ03EG6Z.corp.alleninstitute.org"
    prefixPath      = "e:\\Documents"
    sessionFolder   = os.path.join(prefixPath, "data\\M33\\raw\\data\\Ribbon0004\\session01")

    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", render_host, renderProjectName)

    run(firstsection, lastsection, sessionFolder, renderProject, prefixPath)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time in create_stitched_sections.py: " + timeDuration + " minutes")
