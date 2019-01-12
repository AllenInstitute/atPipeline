import os
import subprocess
import posixpath
import atutils as u
import timeit
import json

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    dataOutputFolder       = os.path.join(projectRoot, p.dataOutputFolder, "rough_aligned")
    input_json     = os.path.join(dataOutputFolder, "roughalignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))
    output_json    = os.path.join(dataOutputFolder, "output_roughalignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

    #stacks
    lowresStack       = "LR_DRP_STI_Session%d"%(session)
    roughalignedStack = "RA_Session%d"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.renderProjectName)

	#point match collections
    lowresPmCollection = "%s_lowres_round"%renderProject.name

    with open(u.alignment_template) as json_data:
       ra = json.load(json_data)

    #Create folder if not exists
    if os.path.isdir(dataOutputFolder) == False:
        os.mkdir(dataOutputFolder)

    u.saveroughalignjson(ra, input_json, "w10dtmj03eg6z.corp.alleninstitute.org" , 80, renderProject.owner, renderProject.name, lowresStack, lowresPmCollection, roughalignedStack, p.clientScripts, p.logLevel, p.firstSection, p.lastSection, u.toDockerMountedPath(dataOutputFolder, p.prefixPath))

    #Run docker command
    cmd = "docker exec " + "rpa-master"
    cmd = cmd + " python -m rendermodules.solver.solve"
    cmd = cmd + " --input_json %s" %(u.toDockerMountedPath(input_json, p.prefixPath))
    cmd = cmd + " --output_json %s"%(u.toDockerMountedPath(output_json, p.prefixPath))

    #Run =============
    print ("Running: " + cmd)
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

