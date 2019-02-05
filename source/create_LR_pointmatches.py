import os
import subprocess
import posixpath
import atutils as u
import timeit

def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    #output directories
    downsample_dir   = os.path.join(projectRoot, p.dataOutputFolder, "low_res")

    #point match collections
    lowres_pm_collection = "%s_LowRes_3D"%renderProject.name

    jsondir  = os.path.join(projectRoot, p.dataOutputFolder, "lowres_tilepairfiles")
    jsonfile = os.path.join(jsondir, "tilepairs-%d-%d-%d-nostitch-EDIT.json"     %(p.zNeighborDistance, p.firstSection, p.lastSection))

    #SIFT Point Match Client
    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " /usr/spark-2.0.2/bin/spark-submit"
    cmd = cmd + " --conf spark.default.parallelism=4750"
    cmd = cmd + " --driver-memory 19g"
    cmd = cmd + " --executor-memory 50g"
    cmd = cmd + " --executor-cores 44"
    cmd = cmd + " --class org.janelia.render.client.spark.SIFTPointMatchClient"
    cmd = cmd + " --name PointMatchFull"
    cmd = cmd + " --master local[*] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.0.2-SNAPSHOT-standalone.jar"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(p.renderHost, p.port)
    cmd = cmd + " --collection %s_lowres_round"             %(p.projectName)
    cmd = cmd + " --owner %s"                               %(p.renderProjectOwner)
    cmd = cmd + " --pairJson %s"                            %(u.toDockerMountedPath(jsonfile, p.prefixPath))
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

