import os
import subprocess
import posixpath
import at_utils as u
import timeit
import logging
logger = logging.getLogger('atPipeline')

def run(p : u.ATDataIni, sessionFolder):
    logger.info("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    rp     = p.renderProject

    #output directories
    downsample_dir   = os.path.join(projectRoot, p.dataOutputFolder, "low_res")

    jsondir  = os.path.join(projectRoot, p.dataOutputFolder, "lowres_tilepairfiles")
    jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch-EDIT.json"     %(p.sys.zNeighborDistance, p.firstSection, p.lastSection))

    #SIFT Point Match Client
    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " /usr/spark-2.0.2/bin/spark-submit"
    cmd = cmd + " --conf spark.default.parallelism=4750"
    cmd = cmd + " --driver-memory %s"                       %(p.sys.SPARK['driverMemory'])
    cmd = cmd + " --executor-memory %s"                     %(p.sys.SPARK['executorMemory'])
    cmd = cmd + " --executor-cores %s"                      %(p.sys.SPARK['executorCores'])

    cmd = cmd + " --class org.janelia.render.client.spark.SIFTPointMatchClient"
    cmd = cmd + " --name PointMatchFull"
    cmd = cmd + " --master local[*] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.1.0-SNAPSHOT-standalone.jar"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(rp.host, rp.hostPort)
    cmd = cmd + " --collection %s_lowres_round"             %(rp.projectName)
    cmd = cmd + " --owner %s"                               %(rp.owner)
    cmd = cmd + " --pairJson %s"                            %(u.toDockerMountedPath(jsonfile, p))
    cmd = cmd + " --renderWithFilter true"
    cmd = cmd + " --maxFeatureCacheGb 40"
    cmd = cmd + " --matchModelType RIGID"
    cmd = cmd + " --matchMinNumInliers 15"
    #cmd = cmd + " --matchMaxEpsilon 15.0"
    #cmd = cmd + " --matchMaxTrust 1.0"

    cmd = cmd + " --SIFTmaxScale 0.85"
    cmd = cmd + " --SIFTminScale 0.7"
    cmd = cmd + " --SIFTsteps 5"
    cmd = cmd + " --renderScale 1.0"
    cmd = cmd + " --matchRod 0.5"
    #cmd = cmd + " --matchFilter CONSENSUS_SETS"

    #Run =============
    u.runPipelineStep(cmd, __file__)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
