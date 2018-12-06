import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)

    #Output directories
    median_dir       = os.path.join("%s"%projectroot, "processed", "medians")
    median_json       = os.path.join(median_dir, "median_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

    #Make sure output folder exist
    if os.path.isdir(median_dir) == False:
       os.mkdir(median_dir)

    #stacks
    acq_stack        = "ACQ_Session%d"%(session)
    median_stack     = "MED_Session%d"%(session)

    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", p.renderHost, renderProjectName)

    with open(atutils.median_template) as json_data:
         med = json.load(json_data)

    atutils.savemedianjson(med, median_json, renderProject.host, renderProject.owner, renderProject.name, acq_stack, median_stack, atutils.toDockerMountedPath(median_dir, p.prefixPath), ribbon*100 + p.firstSection, ribbon*100 + p.lastSection, True)

    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
    cmd = cmd + " --render.port 80"
    cmd = cmd + " --input_json %s"%(atutils.toDockerMountedPath(median_json,  p.prefixPath))

    #Run =============
    print ("Running: " + cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)


if __name__ == "__main__":
    timeStart = timeit.default_timer()
    f = os.path.join('..', 'ATData_params.ini')
    p = atutils.ATDataIni(f)

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")