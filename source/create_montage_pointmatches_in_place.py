##Create new
import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

##Create a new stack with "consolidated" transforms
def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    d_str = "docker exec renderapps_develop "
    render_str = "--render.host %s --render.client_scripts %s --render.port %d --render.memGB %s --log_level %s "%(host,client_scripts,port,memGB,loglevel)
    project_str = "--render.project %s --render.owner %s" %(project, owner)

    #2D point matches
    delta = 150
    minZ = 0
    maxZ = numberofsections
    pm2dstack = "Rough_Aligned_1_DAPI_1"
    highres_pm_collection_2D = "%s_DAPI_1_highres_2D_new"%(project)

    twoD_str = "--minZ %d --maxZ %d --delta %d --dataRoot %s --stack %s --matchCollection %s"%(minZ, maxZ, delta, rootdir, pm2dstack, highres_pm_collection_2D)
    cmd_2D = "%s python -m renderapps.stitching.create_montage_pointmatches_in_place %s %s %s"%(d_str, render_str,project_str, twoD_str)
    print cmd_2D

    cmd_cons = "docker exec "

    # Run =============
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

