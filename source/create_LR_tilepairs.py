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
    inputStack = "S%d_Stitched_Dropped_LowRes"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)
    jsondir           = os.path.join(p.dataOutputFolder,            "lowres_tilepairfiles")
    docker_jsondir    = posixpath.join(p.dockerDataOutputFolder,    "lowres_tilepairfiles")

    # Make sure output folder exist
    if os.path.isdir(jsondir) == False:
        os.mkdir(jsondir)

    jsonfile = "tilepairs-%d-%d-%d-nostitch.json"     %(p.zNeighborDistance, p.firstSection, p.lastSection)

    #Run the TilePairClient
    cmd = "docker exec " + p.atCoreContainer
    cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.0-SNAPSHOT-standalone.jar"
    cmd = cmd + " org.janelia.render.client.TilePairClient"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(p.renderHost, p.renderHostPort)
    cmd = cmd + " --owner %s"							    %(renderProject.owner)
    cmd = cmd + " --project %s"                             %(renderProject.name)
    cmd = cmd + " --stack %s"                               %(inputStack)
    cmd = cmd + " --minZ %d"                                %(p.firstSection)
    cmd = cmd + " --maxZ %d"                                %(p.lastSection)
    cmd = cmd + " --toJson %s"                              %(posixpath.join(docker_jsondir, jsonfile))
    cmd = cmd + " --excludeCornerNeighbors %s"              %(p.excludeCornerNeighbors)
    cmd = cmd + " --excludeSameSectionNeighbors %s"         %(p.excludeSameSectionNeighbors)
    cmd = cmd + " --zNeighborDistance %s"                   %(p.zNeighborDistance)
    cmd = cmd + " --xyNeighborFactor %s"                    %(p.xyNeighborFactor)

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("org.janelia.render.client.TilePairClient threw an Exception")

    #Prepare json file for the SIFTPointMatch Client
    jsonfileedit      = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch-EDIT.json"%(p.zNeighborDistance, p.firstSection, p.lastSection))
    jsonfile          = os.path.join(jsondir, jsonfile)
    copyfile(jsonfile, jsonfileedit)

    for line in fileinput.input(jsonfileedit, inplace=True):
      print (line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)

