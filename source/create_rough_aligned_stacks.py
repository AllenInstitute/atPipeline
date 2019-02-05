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
    inputStack     = "S%d_Stitched_Dropped_LowRes"%(session)
    outputStack    = "S%d_RoughAligned_LowRes"%(session)

    renderProject  = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

	#point match collections
    lowresPmCollection = "%s_lowres_round"%renderProject.name

    with open(u.alignment_template) as json_data:
       ra = json.load(json_data)

    #Create folder if not exists
    if os.path.isdir(dataOutputFolder) == False:
        os.mkdir(dataOutputFolder)

    u.saveRoughAlignJSON(ra, input_json, p.renderHost, 80, renderProject.owner, renderProject.name, inputStack, outputStack, lowresPmCollection, p.clientScripts, p.logLevel, p.firstSection, p.lastSection, u.toDockerMountedPath(dataOutputFolder, p.prefixPath))

    #Run docker command
    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " python -m rendermodules.solver.solve"
    cmd = cmd + " --input_json %s" %(u.toDockerMountedPath(input_json, p.prefixPath))
    cmd = cmd + " --output_json %s"%(u.toDockerMountedPath(output_json, p.prefixPath))

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

