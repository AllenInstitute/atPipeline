import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit

def run(firstsection, lastsection, sessionFolder, dockerContainer, renderProject):

    [dataRootFolder, ribbon, session] = atutils.parse_session_folder(sessionFolder)

    json_prefix = os.path.join("%s"%(dataRootFolder), "logs")
    json_postfix = "_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, firstsection)

    medianfile       = os.path.join(json_prefix, "median"    + json_postfix)

    #stacks
    acq_stack        = "ACQ_Session%d"%(session)
    median_stack     = "MED_Session%d"%(session)
    #flatfield_stack  = "FF_Session%d"%(session)
    #stitched_stack   = "STI_FF_Session%d"%(session)

    #Output directories
    median_dir       = os.path.join("%s"%dataRootFolder, "processed", "Medians_Test")

##        with open(stitchingtemplate) as json_data:
##             sti = json.load(json_data)

    #Create 'logs' folder
    logsFolder=os.path.join(dataRootFolder, "logs")
    if os.path.isdir(logsFolder) == False:
       os.mkdir(logsFolder)

    with open(atutils.mediantemplate) as json_data:
         med = json.load(json_data)

    atutils.savemedianjson(med, medianfile, render_host, renderProject.owner, renderProject.name, acq_stack, median_stack, atutils.toPosixPath(median_dir, "/mnt"), ribbon*100 + firstsection -1, ribbon*100 + lastsection -1, True)

    #Run =============
    cmd = "docker exec " + dockerContainer + " python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
    cmd = cmd + " --render.port 80"
    cmd = cmd + " --input_json %s"%(atutils.toPosixPath(medianfile, "/mnt"))
    print ("Running: " + cmd)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print (line)

if __name__ == "__main__":
    timeStart = timeit.default_timer()
    firstsection = 1
    lastsection = 24

    render_host = "W10DTMJ03EG6Z.corp.alleninstitute.org"
    dataRootFolder = "F:\\data\\M33"
    sessionFolder= os.path.join(dataRootFolder, "raw", "data", "Ribbon0004", "session01")

    dockerContainer = "renderapps_multchan"
    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", "W10DTMJ03EG6Z.corp.alleninstitute.org", renderProjectName)

    projectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    run(firstsection, lastsection, sessionFolder, dockerContainer, renderProject)
    timeEnd = timeit.default_timer()

    print("Elapsed time in time create_median_files: " + str(timeEnd - timeStart))
