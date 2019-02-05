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
    dataOutputFolder       = os.path.join(projectRoot, p.dataOutputFolder, "fine_aligned")
    input_json     = os.path.join(dataOutputFolder, "input_fine_alignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))
    output_json    = os.path.join(dataOutputFolder, "output_fine_alignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

    #stacks
    input_stack       = "S%d_RoughAligned_Consolidated"%(session)
    output_stack      = "S%d_FineAligned"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

	#point match collections
    match_collection_name = "%s_HR_3D"%(renderProject.name)

    with open(u.fine_alignment_template) as json_data:
       ra = json.load(json_data)

    #Create folder if not exists
    if os.path.isdir(dataOutputFolder) == False:
        os.mkdir(dataOutputFolder)

    u.saveFineAlignJSON(ra, input_json, p.renderHost, 80, renderProject.owner, renderProject.name, input_stack, output_stack, match_collection_name, output_stack, p.clientScripts, p.logLevel, p.firstSection, p.lastSection, u.toDockerMountedPath(dataOutputFolder, p.prefixPath))

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
