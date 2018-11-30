import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit

def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)

	# output directories
    dropped_dir = "%s/processed/dropped" % (projectroot)

	# Make sure output folder exist
    if os.path.isdir(dropped_dir) == False:
       os.mkdir(dropped_dir)

	# stacks
    acquisition_Stack       = "ACQ_Session%d"     % (session)
    stitched_dapi_Stack     = "STI_Session%d"     % (session)
    dropped_dapi_Stack      = "DRP_STI_Session%d" % (session)

    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", p.renderHost, renderProjectName)

    # command string
    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " python -m renderapps.stitching.detect_and_drop_stitching_mistakes"
    cmd = cmd + " --render.host %s"                         %(renderProject.host)
    cmd = cmd + " --render.client_scripts %s"               %(p.clientScripts)
    cmd = cmd + " --render.port %d"                         %(p.port)
    cmd = cmd + " --render.memGB %s"                        %(p.memGB)
    cmd = cmd + " --log_level %s"                           %(p.logLevel)
    cmd = cmd + " --render.project %s"                      %(renderProject.name)
    cmd = cmd + " --render.owner %s"                        %(renderProject.owner)
    cmd = cmd + " --prestitchedStack %s"                    %(acquisition_Stack)
    cmd = cmd + " --poststitchedStack %s"                   %(stitched_dapi_Stack)
    cmd = cmd + " --outputStack %s"                         %(dropped_dapi_Stack)
    cmd = cmd + " --jsonDirectory %s"                       %(atutils.toDockerMountedPath(dropped_dir, p.prefixPath))
    cmd = cmd + " --edge_threshold %d"                      %(p.edgeThreshold)
    cmd = cmd + " --pool_size %d"                           %(p.poolSize)
    cmd = cmd + " --distance_threshold %d"                  %(p.distance)

    # docker commands
    print (cmd)

    # Run =============
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

