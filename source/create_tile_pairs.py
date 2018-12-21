import os
import subprocess
import posixpath
import lib.atutils as u
import timeit
from shutil import copyfile

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
    lowres_stack = "LR_DRP_STI_Session%d"%(session)

    renderProjectName = u.getProjectNameFromSessionFolder(sessionFolder)
    renderProject = u.RenderProject(p.renderProjectOwner, p.renderHost, renderProjectName)


    JSONDIR = "%s/processed/tilepairfiles1"%(projectRoot)

    JSONFILE=    JSONDIR  + "/tilepairs-%d-%d-%d-nostitch.json"%(p.)
    JSONFILEEDIT=JSONDIR + "/tilepairs-10-0-23-nostitch-EDIT.json"

    #Run the TilePairClient
    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.0.1-SNAPSHOT-standalone.jar"
    cmd = cmd + " org.janelia.render.client.TilePairClient"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(p.renderHost, p.port)
    cmd = cmd + " --owner %s"							    %renderProject.owner
    cmd = cmd + " --project %s"                             %renderProject.name
    cmd = cmd + " --stack %s"%(lowres_stack)
    cmd = cmd + " --minZ %d"%(p.firstSection)
    cmd = cmd + " --maxZ  %d"%(p.lastSection)
    cmd = cmd + " --toJson %s"%JSONFILE
    cmd = cmd + " --excludeCornerNeighbors true"
    cmd = cmd + " --zNeighborDistance 1"
    cmd = cmd + " --excludeSameSectionNeighbors true"
    cmd = cmd + " --xyNeighborFactor 0.01"

    #Run =============
    print ("Running: " + cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    #copyfile(JSONFILE, JSONFILEEDIT)

if __name__ == "__main__":
    timeStart = timeit.default_timer()
    f = os.path.join('..', 'ATData.ini')
    p = u.ATDataIni(f)

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)
    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")

