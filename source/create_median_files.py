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
    median_dir       = os.path.join("%s"%dataRootFolder, "processed", "medians")
    median_json       = os.path.join(median_dir, "median_%s_%s_%d_%d.json"%(ribbon, session, firstsection-1, lastsection-1))

    #stacks
    acq_stack        = "ACQ_Session%d"%(session)
    median_stack     = "MED_Session%d"%(session)

    #Make sure output folder exist
    if os.path.isdir(median_dir) == False:
       os.mkdir(median_dir)

    with open(atutils.mediantemplate) as json_data:
         med = json.load(json_data)

    atutils.savemedianjson(med, median_json, renderProject.host, renderProject.owner, renderProject.name, acq_stack, median_stack, atutils.toDockerMountedPath(median_dir, prefixPath), ribbon*100 + firstsection -1, ribbon*100 + lastsection -1, True)

    #Run =============
    cmd = "docker exec " + dockerContainer + " python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
    cmd = cmd + " --render.port 80"
    cmd = cmd + " --input_json %s"%(atutils.toDockerMountedPath(median_json,  prefixPath))
    print ("Running: " + cmd)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print (line)

if __name__ == "__main__":
    timeStart = timeit.default_timer()
    firstsection = 1
    lastsection = 2

    render_host = "W10DTMJ03EG6Z.corp.alleninstitute.org"

    prefixPath = "e:\\Documents"
    sessionFolder = os.path.join(prefixPath, "data\\M33\\raw\\data\\Ribbon0004\\session01")

    dockerContainer = "renderapps_multchan"
    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", render_host, renderProjectName)

    projectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    run(firstsection, lastsection, sessionFolder, dockerContainer, renderProject, prefixPath)
    timeEnd = timeit.default_timer()

    print("Elapsed time in time create_median_files: " + str(timeEnd - timeStart))
