import os
import subprocess
import posixpath
import atutils as u
import timeit
import fileinput
from shutil import copyfile

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
    input_stack = "S%d_RoughAligned_Consolidated"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)
    jsonOutputFolder  = os.path.join(projectRoot, p.dataOutputFolder, "high_res_tilepairfiles")

    # Make sure that the output folder exist
    if os.path.isdir(jsonOutputFolder) == False:
        os.mkdir(jsonOutputFolder)

    jsonfile = os.path.join(jsonOutputFolder, "tilepairs-%d-%d-%d-nostitch.json"     %(p.zNeighborDistance, p.firstSection, p.lastSection))

    #Run the TilePairClient
    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.0.3-SNAPSHOT-standalone.jar"
    cmd = cmd + " org.janelia.render.client.TilePairClient"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(p.renderHost, p.port)
    cmd = cmd + " --owner %s"							    %(renderProject.owner)
    cmd = cmd + " --project %s"                             %(renderProject.name)
    cmd = cmd + " --stack %s"                               %(input_stack)
    cmd = cmd + " --minZ %d"                                %(p.firstSection)
    cmd = cmd + " --maxZ %d"                                %(p.lastSection)
    cmd = cmd + " --toJson %s"                              %(u.toDockerMountedPath(jsonfile, p.prefixPath))
    cmd = cmd + " --excludeCornerNeighbors %s"              %(p.excludeCornerNeighbors)
    cmd = cmd + " --excludeSameSectionNeighbors %s"         %(p.excludeSameSectionNeighbors)
    cmd = cmd + " --zNeighborDistance %s"                   %(p.zNeighborDistance)
    cmd = cmd + " --xyNeighborFactor %s"                    %(p.xyNeighborFactor)

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    #Prepare json file for the SIFTPointMatch Client
    jsonfileedit      = os.path.join(jsonOutputFolder, "tilepairs-%d-%d-%d-nostitch-EDIT.json"%(p.zNeighborDistance, p.firstSection, p.lastSection))
    copyfile(jsonfile, jsonfileedit)
    for line in fileinput.input(jsonfileedit, inplace=True):
      print (line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")

if __name__ == "__main__":
    timeStart = timeit.default_timer()
    f = os.path.join('..', 'ATData.ini')
    p = u.ATDataIni(f)

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")