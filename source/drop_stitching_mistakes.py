import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

def run(p : u.ATDataIni, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

	# output directories
    dropped_dir = os.path.join(projectroot, p.dataOutputFolder, "dropped")

	# Make sure output folder exist
    if os.path.isdir(dropped_dir) == False:
       os.mkdir(dropped_dir)

	# stacks
    acquisition_Stack       = "S%d_Session%d"    %(session, session)
    stitched_dapi_Stack     = "S%d_Stitched"     %(session)
    dropped_dapi_Stack      = "S%d_Stitched_Dropped" %(session)

    rp     = p.renderProject

    # command string
    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " python -m renderapps.stitching.detect_and_drop_stitching_mistakes"
    cmd = cmd + " --render.owner %s"                        %(rp.owner)
    cmd = cmd + " --render.host %s"                         %(rp.host)
    cmd = cmd + " --render.project %s"                      %(rp.projectName)
    cmd = cmd + " --render.client_scripts %s"               %(rp.clientScripts)
    cmd = cmd + " --render.port %d"                         %(rp.hostPort)
    cmd = cmd + " --render.memGB %s"                        %(rp.memGB)
    cmd = cmd + " --log_level %s"                           %(rp.logLevel)
    cmd = cmd + " --prestitchedStack %s"                    %(acquisition_Stack)
    cmd = cmd + " --poststitchedStack %s"                   %(stitched_dapi_Stack)
    cmd = cmd + " --outputStack %s"                         %(dropped_dapi_Stack)
    cmd = cmd + " --jsonDirectory %s"                       %(u.toDockerMountedPath(dropped_dir, p))
    cmd = cmd + " --edge_threshold %d"                      %(p.sys.edgeThreshold)
    cmd = cmd + " --pool_size %d"                           %(p.sys.atCoreThreads)
    cmd = cmd + " --distance_threshold %d"                  %(p.sys.distance)

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




