##Create new
import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

##Create 2D pointmatches for overlapping tiles
def run(p : u.ATDataIni, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    rp = p.renderProject
    outputFolder  = os.path.join(projectRoot, p.dataOutputFolder)

    match_collection_name = "%s_HR_2D"%(rp.projectName)
    delta = 250

    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " python -m renderapps.stitching.create_montage_pointmatches_in_place"
    cmd = cmd + " --render.host %s"                           %(rp.host)
    cmd = cmd + " --render.project %s"                        %(rp.projectName)
    cmd = cmd + " --render.owner %s"                          %(rp.owner)
    cmd = cmd + " --render.client_scripts %s"                 %(rp.clientScripts)
    cmd = cmd + " --render.memGB %s"                          %(rp.memGB)
    cmd = cmd + " --render.port %s"                           %(rp.hostPort)
    cmd = cmd + " --pool_size %s"                             %(p.sys.atCoreThreads)
    cmd = cmd + " --stack S%d_RoughAligned"                   %(session)
    cmd = cmd + " --minZ %d"                                  %(p.firstSection)
    cmd = cmd + " --maxZ %d"                                  %(p.lastSection)
    cmd = cmd + " --dataRoot %s"                              %(u.toDockerMountedPath(outputFolder, p))
    cmd = cmd + " --matchCollection %s"                       %(match_collection_name)
    cmd = cmd + " --delta %d"                                 %(delta)
    cmd = cmd + " --output_json Test"

    # Run =============
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

