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

	# output directories
    dropped_dir = os.path.join(p.dataOutputFolder, "dropped")

	# Make sure output folder exist
    if os.path.isdir(dropped_dir) == False:
       os.mkdir(dropped_dir)

	# stacks
    acquisition_Stack       = "S%d_Session%d"    %(session, session)
    stitched_dapi_Stack     = "S%d_Stitched"     %(session)
    dropped_dapi_Stack      = "S%d_Stitched_Dropped" %(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    # command string
    cmd = "docker exec " + p.atCoreContainer
    cmd = cmd + " python -m renderapps.stitching.detect_and_drop_stitching_mistakes"
    cmd = cmd + " --render.owner %s"                        %(renderProject.owner)
    cmd = cmd + " --render.host %s"                         %(renderProject.host)
    cmd = cmd + " --render.project %s"                      %(renderProject.name)
    cmd = cmd + " --render.client_scripts %s"               %(p.clientScripts)
    cmd = cmd + " --render.port %d"                         %(p.renderHostPort)
    cmd = cmd + " --render.memGB %s"                        %(p.memGB)
    cmd = cmd + " --log_level %s"                           %(p.logLevel)
    cmd = cmd + " --prestitchedStack %s"                    %(acquisition_Stack)
    cmd = cmd + " --poststitchedStack %s"                   %(stitched_dapi_Stack)
    cmd = cmd + " --outputStack %s"                         %(dropped_dapi_Stack)
    cmd = cmd + " --jsonDirectory %s"                       %(posixpath.join(p.dockerDataOutputFolder, "dropped"))
    cmd = cmd + " --edge_threshold %d"                      %(p.edgeThreshold)
    cmd = cmd + " --pool_size %d"                           %(p.poolSize)
    cmd = cmd + " --distance_threshold %d"                  %(p.distance)

    # Run =============
    print ("Running: " + cmd.replace('--', '\n--'))

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
    	print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("Error generating median files")

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)




