import os
import subprocess
import timeit
import atutils as u

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    for sectnum in range(p.firstSection, p.lastSection + 1):
        print("Processing section: " + str(sectnum))

        #State table file
        statetablefile = p.getStateTableFileName(ribbon, session, sectnum)
        print("Creating statetable file: " + statetablefile)

        if os.path.exists(statetablefile):
           print("The statetable: " + statetablefile + " already exists. Continuing..")
        else:
            cmd = "docker exec " + p.rpaContainer
            cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"%(u.toDockerMountedPath(projectroot,  p.prefixPath))
            cmd = cmd + " --outputFile %s"%(u.toDockerMountedPath(statetablefile,     p.prefixPath))
            cmd = cmd + " --ribbon %d"%ribbon
            cmd = cmd + " --session %d"%session
            cmd = cmd + " --section %d"%(sectnum)
            cmd = cmd + " --oneribbononly True"

		    #Run ====================
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