import os
import sys
import subprocess
import platform
import posixpath
import atutils

def run(sessionFolder, firstsection, lastsection, dockerContainer, prefixPath):

    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)
    print ("Processing session folder: " + sessionFolder)

    for sectnum in range(firstsection, lastsection+1):
        print("Processing section: " + str(sectnum))

        #create state table file name
        statetablefile =  "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum -1)
        statetablefile = projectroot + os.path.join("scripts", statetablefile)

        if os.path.exists(statetablefile):
           print("The statetable: " + statetablefile + " already exists. Continuing..")
        else:
            #Example data
            #docker exec renderapps python /pipeline/make_state_table_ext_multi_pseudoz.py
            #--projectDirectory /mnt/data/M33
            #--outputFile  /mnt/data/M33/statetables/test
            #--oneribbononly True
            #--ribbon 4
            #--session 1
            #--section 0

            #make state table
            #Need to pass posix paths to docker
            cmd = "docker exec " + dockerContainer
            cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"%(atutils.toDockerMountedPath(projectroot,  prefixPath))
            cmd = cmd + " --outputFile %s"%(atutils.toDockerMountedPath(statetablefile, prefixPath))
            cmd = cmd + " --ribbon %d"%ribbon
            cmd = cmd + " --session %d"%session
            cmd = cmd + " --section %d"%(sectnum - 1) #Start at 0
            cmd = cmd + " --oneribbononly True"
            print ("Running: " + cmd)

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                print (line)


if __name__ == "__main__":
    firstsection = 1
    lastsection = 1

    prefixPath = "/Users/synbio/Documents"
    sessionFolder = os.path.join(prefixPath, "data/M33/raw/data/Ribbon0004/session01") 
    dockerContainer = "renderapps_multchan"

    run(sessionFolder, firstsection, lastsection, dockerContainer, prefixPath)
    print ("Finished creation of state tables")
