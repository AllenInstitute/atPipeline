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
    flatfield_stack  = "FF_Session%d"%(session)
    stitched_stack   = "STI_Session%d"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.renderProjectName)

	#Create json files and start stitching...
    for sectnum in range(p.firstSection, p.lastSection + 1):

        with open(u.stitching_template) as json_data:
             stitching_template = json.load(json_data)

        stitching_json = os.path.join(stitching_dir, "flatfield""_%s_%s_%s_%d.json"%(renderProject.name, ribbon, session, sectnum))
        z = ribbon*100 + sectnum

        u.savestitchingjson(stitching_template, stitching_json, renderProject.owner, renderProject.name, flatfield_stack, stitched_stack, z, p.renderHost)

        cmd = "docker exec " + p.atmContainer
        cmd = cmd + " java -cp ./target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC"
        cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(stitching_json, p.prefixPath))

        #Run =============
        print ("Running: " + cmd.replace('--', '\n--'))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout.readlines():
            print (line)

if __name__ == "__main__":
    timeStart = timeit.default_timer()
    f = os.path.join('..', 'ATData.ini')
    p = u.ATDataIni(f)

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")