import os
import json
import sys
import subprocess
import posixpath
import lib.atutils as u
import timeit


def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
    firstRibbon = ribbon
    lastRibbon = int(p.ribbons[-1][6:])

    # output directories
    downsample_dir = "%s/processed/Low_res"%(projectRoot)
    numsections_file = "%s/numsections"%downsample_dir

    # Make sure output folder exist
    if os.path.isdir(downsample_dir) == False:
        os.mkdir(downsample_dir)

    # stacks
    dropped_dapi_Stack = "DRP_STI_Session%d" % (session)
    lowres_stack = "LR_DRP_STI_Session%d"%(session)

    renderProjectName = u.getProjectNameFromSessionFolder(sessionFolder)
    renderProject = u.RenderProject("ATExplorer", p.renderHost, renderProjectName)

    # docker commands
    cmd = "docker exec " + p.rpaContainer
    cmd = cmd + " python -m renderapps.materialize.make_downsample_image_stack_multi"
    #cmd = cmd + " python -m renderapps.materialize.make_downsample_image_stack"
    cmd = cmd + " --render.port %s"                                %p.port
    cmd = cmd + " --render.host %s"                                %renderProject.host
    cmd = cmd + " --render.client_scripts %s"                      %p.clientScripts
    cmd = cmd + " --render.memGB %s"                               %p.memGB
    cmd = cmd + " --log_level %s"                                  %p.logLevel
    cmd = cmd + " --render.project %s"                             %renderProject.name
    cmd = cmd + " --render.owner %s"                               %renderProject.owner
    cmd = cmd + " --input_stack %s"                                %dropped_dapi_Stack
    cmd = cmd + " --output_stack %s"                               %lowres_stack
    cmd = cmd + " --image_directory %s"                            %(u.toDockerMountedPath(downsample_dir, p.prefixPath))
    cmd = cmd + " --pool_size %s"                                  %p.poolSize
    cmd = cmd + " --scale %s"                                      %p.scale
    cmd = cmd + " --minZ %s"                                       %(firstRibbon*100)
    cmd = cmd + " --maxZ %s"                                       %((lastRibbon + 1)*100 - 1)
    cmd = cmd + " --numsectionsfile %s"                            %(u.toDockerMountedPath(numsections_file, p.prefixPath))

    # Run =============
    print ("Running: " + cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for i in range(0,2):
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

