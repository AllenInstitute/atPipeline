import os
import subprocess
import posixpath
import at_utils as u
import timeit
import fileinput
from shutil import copyfile
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):

    logger.info("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
    inputStack = "S%d_LowRes"%(session)

    rp      = p.renderProject
    jsondir = os.path.join(projectRoot, p.dataOutputFolder, "lowres_tilepairfiles")

    # Make sure output folder exist
    if os.path.isdir(jsondir) == False:
        os.mkdir(jsondir)

    jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch.json"     %(p.sys.zNeighborDistance, p.firstSection, p.lastSection))

    #Run the TilePairClient
    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.1.0-SNAPSHOT-standalone.jar"
    cmd = cmd + " org.janelia.render.client.TilePairClient"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
    cmd = cmd + " --owner %s"							    %(rp.owner)
    cmd = cmd + " --project %s"                             %(rp.projectName)
    cmd = cmd + " --stack %s"                               %(inputStack)
    cmd = cmd + " --minZ %d"                                %(p.firstSection)
    cmd = cmd + " --maxZ %d"                                %(p.lastSection)
    cmd = cmd + " --toJson %s"                              %(u.toDockerMountedPath(jsonfile, p))
    cmd = cmd + " --excludeCornerNeighbors %s"              %(p.sys.excludeCornerNeighbors)
    cmd = cmd + " --excludeSameSectionNeighbors %s"         %(p.sys.excludeSameSectionNeighbors)
    cmd = cmd + " --zNeighborDistance %s"                   %(p.sys.zNeighborDistance)
    cmd = cmd + " --xyNeighborFactor %s"                    %(p.sys.xyNeighborFactor)

    #Run =============
    u.runPipelineStep(cmd, __file__)

    #Prepare json file for the SIFTPointMatch Client
    jsonfileedit      = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch-EDIT.json"%(p.sys.zNeighborDistance, p.firstSection, p.lastSection))
    copyfile(jsonfile, jsonfileedit)

    for line in fileinput.input(jsonfileedit, inplace=True):
        print(line.replace("render-parameters", "render-parameters?removeAllOption=true"), end="")

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
