import os
import subprocess
import posixpath
import atutils as u
import timeit
import json

def run(p : u.ATDataIni, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Output directories
    dataOutputFolder       = os.path.join(projectRoot, p.dataOutputFolder, "fine_aligned")
    input_json     	= os.path.join(dataOutputFolder, "input_fine_alignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))
    output_json    	= os.path.join(dataOutputFolder, "output_fine_alignment_%s_%s_%d_%d.json"%(ribbon, session, p.firstSection, p.lastSection))

    #stacks
    input_stack       = "S%d_RoughAligned_Consolidated"%(session)
    output_stack      = "S%d_FineAligned"%(session)

    rp     = p.renderProject

	#point match collections
    pm_collection2D     = "%s_HR_2D"%(rp.projectName)
    pm_collection3D     = "%s_HR_3D"%(rp.projectName)

    with open(p.systemParameters.fine_alignment_template) as json_data:
       ra = json.load(json_data)

    #Create folder if not exists
    if os.path.isdir(dataOutputFolder) == False:
        os.mkdir(dataOutputFolder)

    u.saveFineAlignJSON(ra, input_json, rp.host, rp.hostPort, rp.owner, rp.projectName,
                            input_stack, output_stack, pm_collection2D, pm_collection3D,
                            rp.clientScripts, rp.logLevel, p.firstSection, p.lastSection, u.toDockerMountedPath(dataOutputFolder, p))

    #Run docker command
    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " python -m rendermodules.solver.solve"
    cmd = cmd + " --input_json %s" %(u.toDockerMountedPath(input_json, p))
    cmd = cmd + " --output_json %s"%(u.toDockerMountedPath(output_json, p))

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception(os.path.basename(__file__) + " threw an Exception")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
