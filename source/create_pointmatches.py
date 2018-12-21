import os
import subprocess
import posixpath
import atutils as u
import timeit


def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    # output directories
    downsample_dir   = os.path.join(projectRoot, p.dataOutputFolder, "low_res")
    numsections_file = os.path.join(downsample_dir, "numsections")

    # stacks
    lowres_stack = "LR_DRP_STI_Session%d"%(session)

    renderProjectName = u.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, renderProjectName)

    #point match collections
    lowres_pm_collection = "%s_Lowres_3D"%renderProject.name

    #get numsections
    f = open(numsections_file)
    numSections = int(f.readline())
    print ("Number of sections to create pointmatches for: " + str(numSections))

    jsondir  = os.path.join(projectRoot, p.dataOutputFolder, "tilepairfiles")
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
    cmd = cmd + " --master local[*] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.0.1-SNAPSHOT-standalone.jar"
    cmd = cmd + " --baseDataUrl http://%s:%d/render-ws/v1"  %(p.renderHost, p.port)
    cmd = cmd + " --collection %s_lowres_round"             %(renderProjectName)
    cmd = cmd + " --owner %s"                               %(p.renderProjectOwner)
    cmd = cmd + " --pairJson %s"                            %(u.toDockerMountedPath(jsonfile, p.prefixPath))
    cmd = cmd + " --renderWithFilter true"
    cmd = cmd + " --maxFeatureCacheGb 40"
    cmd = cmd + " --matchModelType RIGID"
    cmd = cmd + " --matchMinNumInliers 8"
    cmd = cmd + " --SIFTmaxScale 1.0"
    cmd = cmd + " --SIFTminScale 0.8"
    cmd = cmd + " --SIFTsteps 7"
    cmd = cmd + " --renderScale 1.0"

    #Run =============
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

