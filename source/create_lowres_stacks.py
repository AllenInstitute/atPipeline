import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit


def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)
    firstRibbon = ribbon
    lastRibbon = int(p.ribbons[-1][6:])

    # output directories
    downsample_dir   = os.path.join(projectRoot, p.dataOutputFolder, "low_res")
    numsections_file = os.path.join(downsample_dir,                   "numsections")

    # Make sure output folder exist
    if os.path.isdir(downsample_dir) == False:
        os.mkdir(downsample_dir)

    # stacks
    input_stack  = "S%d_Stitched_Dropped"   %(session)
    output_stack = "S%d_LowRes"%(session)

    renderProject = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    # docker commands
    cmd = "docker exec " + p.atCoreContainer
    cmd = cmd + " python -m renderapps.materialize.make_downsample_image_stack"
    cmd = cmd + " --render.host %s"                                %(renderProject.host)
    cmd = cmd + " --render.project %s"                             %(renderProject.name)
    cmd = cmd + " --render.owner %s"                               %(renderProject.owner)
    cmd = cmd + " --render.client_scripts %s"                      %(p.clientScripts)
    cmd = cmd + " --render.memGB %s"                               %(p.memGB)
    cmd = cmd + " --render.port %s"                                %(p.renderHostPort)
    cmd = cmd + " --input_stack %s"                                %(input_stack)
    cmd = cmd + " --output_stack %s"                               %(output_stack)
    cmd = cmd + " --image_directory %s"                            %(u.toDockerMountedPath(downsample_dir, p))
    cmd = cmd + " --pool_size %s"                                  %(p.poolSize)
    cmd = cmd + " --scale %s"                                      %(p.scale)
    cmd = cmd + " --minZ %s"                                       %(firstRibbon*100)
    cmd = cmd + " --maxZ %s"                                       %((lastRibbon + 1)*100 - 1)
    cmd = cmd + " --numsectionsfile %s"                            %(u.toDockerMountedPath(numsections_file, p))
    cmd = cmd + " --log_level %s"                                  %(p.logLevel)

    # Run =============
    print ("Running: " + cmd.replace('--', '\n--'))

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception(os.path.basename(__file__) + " threw an Exception")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)

