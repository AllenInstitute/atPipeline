import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit
import time
def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)

    #Output directories
    flatfield_dir    = os.path.join("%s"%projectroot, "processed", "flatfield")

    #Make sure output folder exists
    if os.path.isdir(flatfield_dir) == False:
       os.mkdir(flatfield_dir)

    #stacks
    acq_stack        = "ACQ_Session%d"%(session)
    median_stack     = "MED_Session%d"%(session)
    flatfield_stack  = "FF_Session%d"%(session)

   

    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", p.renderHost, renderProjectName)
	
    #Create json files and apply median.
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(atutils.flatfield_template) as json_data:
             ff = json.load(json_data)

        flatfield_json = os.path.join(flatfield_dir, "flatfield""_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, sectnum))

        z = ribbon*100 + sectnum

        atutils.saveflatfieldjson(ff, flatfield_json, renderProject.host, renderProject.owner, renderProject.name, acq_stack, median_stack, flatfield_stack, atutils.toDockerMountedPath(flatfield_dir, p.prefixPath), z, True)
        cmd = "docker exec " + p.rpaContainer
        cmd = cmd + " python -m rendermodules.intensity_correction.apply_multiplicative_correction"
        cmd = cmd + " --render.port 80"
        cmd = cmd + " --input_json %s"%(atutils.toDockerMountedPath(flatfield_json, p.prefixPath))

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