import os
import sys
import subprocess
import posixpath
import atutils
import timeit

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)


    for sectnum in range(p.firstSection, p.lastSection + 1):
        print("Processing section: " + str(sectnum))

        #State table file
        statetablefile = projectroot + os.path.join("scripts", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum))


        if os.path.exists(statetablefile):
           print("The statetable: " + statetablefile + " already exists. Continuing..")
        else:
            cmd = "docker exec " + p.rpaContainer
            cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"%(atutils.toDockerMountedPath(projectroot,  p.prefixPath))
            cmd = cmd + " --outputFile %s"%(atutils.toDockerMountedPath(statetablefile,     p.prefixPath))
            cmd = cmd + " --ribbon %d"%ribbon
            cmd = cmd + " --session %d"%session
            cmd = cmd + " --section %d"%(sectnum)
            cmd = cmd + " --oneribbononly True"
        
		    #Run =============
            print ("Running: " + cmd)

            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout.readlines():
                print (line)


if __name__ == "__main__":
    timeStart = timeit.default_timer()

    p = atutils.ATDataIni('..\\Tottes.ini')

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")