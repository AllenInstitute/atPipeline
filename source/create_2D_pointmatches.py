##Create new
import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

##Create 2D pointmatches for overlapping tiles
def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)
    outputFolder  = os.path.join(projectRoot, p.dataOutputFolder)

    match_collection_name = "%s_HR"%(renderProject.name)
    delta = 250

    cmd = "docker exec " + p.atCoreContainer
    cmd = cmd + " python -m renderapps.stitching.create_montage_pointmatches_in_place"
    cmd = cmd + " --render.host %s"                           %(renderProject.host)
    cmd = cmd + " --render.project %s"                        %(renderProject.name)
    cmd = cmd + " --render.owner %s"                          %(renderProject.owner)
    cmd = cmd + " --render.client_scripts %s"                 %(p.clientScripts)
    cmd = cmd + " --render.memGB %s"                          %(p.memGB)
    cmd = cmd + " --render.port %s"                           %(p.port)
    cmd = cmd + " --pool_size %s"                             %(p.poolSize)
    cmd = cmd + " --stack S%d_RoughAligned"                   %(session)
    cmd = cmd + " --minZ %d"                                  %(p.firstSection)
    cmd = cmd + " --maxZ %d"                                  %(p.lastSection)
    cmd = cmd + " --dataRoot %s"                              %(u.toDockerMountedPath(outputFolder, p.prefixPath))
    cmd = cmd + " --matchCollection %s"                       %(match_collection_name)
    cmd = cmd + " --delta %d"                                 %(delta)
    cmd = cmd + " --output_json Test"

    # Run =============
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

