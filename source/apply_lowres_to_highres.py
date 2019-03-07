import os
import subprocess
import posixpath
import atutils as u
import timeit
import json

def run(p : u.ATDataIni, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    lowresStack             = "S%d_LowRes"%(session)

    inputStack              = "S%d_Stitched_Dropped"%(session)
    outputStack             = "S%d_RoughAligned"%(session)

    rp                      = p.renderProject
    firstribbon             = p.firstRibbon
    lastribbon              = p.lastRibbon

    roughalign_ts_dir = os.path.join(projectRoot, p.dataOutputFolder, "rough_aligned_tilespecs")

    # Make sure output folder exist
    if os.path.isdir(roughalign_ts_dir) == False:
        os.mkdir(roughalign_ts_dir)

    #Put this in ini file later on..
    scale = 0.05

    #Run docker command
    cmd = "docker exec " + p.sys.atCoreContainer
    cmd = cmd + " python -m renderapps.rough_align.ApplyLowRes2HighRes"
    cmd = cmd + " --render.host %s"                %(rp.host)
    cmd = cmd + " --render.owner %s "              %(rp.owner)
    cmd = cmd + " --render.project %s"             %(rp.projectName)
    cmd = cmd + " --render.client_scripts %s"      %(rp.clientScripts)
    cmd = cmd + " --render.port %d"                %(rp.hostPort)
    cmd = cmd + " --render.memGB %s"               %(rp.memGB)
    cmd = cmd + " --pool_size %d"                  %(p.sys.atCoreThreads)
    cmd = cmd + " --tilespec_directory %s"         %(u.toDockerMountedPath(roughalign_ts_dir, p))
    cmd = cmd + " --scale %s"                      %(p.sys.downSampleScale)
    cmd = cmd + " --input_stack %s"                %(inputStack)
    cmd = cmd + " --lowres_stack %s"               %(lowresStack)
    cmd = cmd + " --prealigned_stack %s"           %(inputStack)
    cmd = cmd + " --output_stack %s"     		   %(outputStack)

    #TODO: get the Z's right..
    cmd = cmd + " --minZ 0"#%d"                  %(p.firstSection*100)
    cmd = cmd + " --maxZ 500"#%d"                  %(p.lastSection*100)
    #cmd = cmd + " --minZ %d --maxZ %d "       %(firstribbon*100, (lastribbon+1) * 100)

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)




