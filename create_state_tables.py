##This script was modified by TK to allow execution from windows.
##This is to be used for testing purposes

import os
import sys
import subprocess
import posixpath
import atutils

def run(sessionFolder, firstsection, lastsection, dockerContainer):

    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)

    print ("Processing session folder: " + sessionFolder)
    for sectnum in range(firstsection,lastsection+1):
        print("Processing section: " + str(sectnum))

        #create state table file name
        statetablefile = projectroot + os.path.join("scripts", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum))

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
            cmd = "docker exec " + dockerContainer + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"%(atutils.toPosixPath(projectroot,  "/mnt"))
            cmd = cmd + " --outputFile %s"%(atutils.toPosixPath(statetablefile, "/mnt"))
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
    lastsection = 24
    sessionFolder = "F:\\data\\M33\\raw\\data\\Ribbon0004\\session01"
    dockerContainer = "renderapps_multchan"

    run(sessionFolder, firstsection, lastsection, dockerContainer)
    print ("Finished creation of state tables")
