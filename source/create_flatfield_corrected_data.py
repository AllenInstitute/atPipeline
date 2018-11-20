import os
import json
import sys
import subprocess
import platform
import posixpath
import atutils
import timeit

def run(firstsection, lastsection, sessionFolder, dockerContainer, renderProject, prefixPath):

    [dataRootFolder, ribbon, session] = atutils.parse_session_folder(sessionFolder)
    #Output directories
    flatfield_dir    = os.path.join("%s"%dataRootFolder, "processed", "flatfield")

    #stacks
    acq_stack        = "ACQ_Session%d"%(session)
    median_stack     = "MED_Session%d"%(session)
    flatfield_stack  = "FF_Session%d"%(session)

    #Make sure output folder exists
    if os.path.isdir(flatfield_dir) == False:
       os.mkdir(flatfield_dir)

	#Create json files and apply median.
    for sectnum in range(firstsection, lastsection + 1):

        with open(atutils.flatfieldtemplate) as json_data:
             ff = json.load(json_data)

        flatfield_json    = os.path.join(flatfield_dir, "flatfield""_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, sectnum))

        z = ribbon*100 + sectnum

        atutils.saveflatfieldjson(ff, flatfield_json, renderProject.host, renderProject.owner, renderProject.name, acq_stack, median_stack, flatfield_stack, atutils.toDockerMountedPath(flatfield_dir, prefixPath), z, True)
        cmd = "docker exec " + dockerContainer + " python -m rendermodules.intensity_correction.apply_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(atutils.toDockerMountedPath(flatfield_json, prefixPath))

        #Run =============
        print ("Running: " + cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print (line)

if __name__ == "__main__":
    timeStart = timeit.default_timer()
    firstsection = 1
    lastsection = 23

    render_host     = "W10DTMJ03EG6Z.corp.alleninstitute.org"
    prefixPath = "e:\\Documents"
    sessionFolder = os.path.join(prefixPath, "data\\M33\\raw\\data\\Ribbon0004\\session01")

    dockerContainer = "renderapps_multchan"

    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", render_host, renderProjectName)

    run(firstsection, lastsection, sessionFolder, dockerContainer, renderProject, prefixPath)

    timeEnd = timeit.default_timer()
    print("Elapsed time in create_flatfield_corrected_data: " + str(timeEnd - timeStart))
