import os
import subprocess
import posixpath
import atutils as u
import timeit
import json

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    lowresStack             = "LR_DRP_STI_Session%d"%(session)
    lowresRoughAlignedStack = "RA_Session%d"%(session)
    inputStack              = "DRP_STI_Session%d"%(session)
    outputStack             = "RAM_Session%d"%(session)
    renderProject           = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)
    firstribbon             = p.firstRibbon
    lastribbon              = p.lastRibbon

    roughalign_ts_dir = os.path.join(projectRoot, p.dataOutputFolder, "rough_aligned_tilespecs")

    # Make sure output folder exist
    if os.path.isdir(roughalign_ts_dir) == False:
        os.mkdir(roughalign_ts_dir)

    #Put this in ini file later on..
    scale = 0.05

    #Run docker command
    cmd = "docker exec " + "rpa"
    cmd = cmd + " python -m renderapps.rough_align.ApplyLowRes2HighRes"
    cmd = cmd + " --render.host %s"                %renderProject.host
    cmd = cmd + " --render.owner %s "              %renderProject.owner
    cmd = cmd + " --render.project %s"             %renderProject.name
    cmd = cmd + " --render.client_scripts %s"      %p.clientScripts
    cmd = cmd + " --render.port %d"                %p.port
    cmd = cmd + " --render.memGB %s"               %p.memGB
    cmd = cmd + " --pool_size %d"                  %(p.poolSize)
    cmd = cmd + " --tilespec_directory %s"         %(u.toDockerMountedPath(roughalign_ts_dir, p.prefixPath))
    cmd = cmd + " --scale %s"                      %scale
    cmd = cmd + " --input_stack %s"                %inputStack
    cmd = cmd + " --lowres_stack %s"               %lowresStack
    cmd = cmd + " --prealigned_stack %s"           %inputStack
    cmd = cmd + " --output_stack RA_Session%d"     %(session)

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
    timeStart = timeit.default_timer()
    f = os.path.join('..', 'ATData.ini')
    p = u.ATDataIni(f)

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")

