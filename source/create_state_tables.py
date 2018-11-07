import os
import sys
import subprocess
import platform
import posixpath
import atutils

def run(sessionFolder, firstsection, lastsection, dockerContainer):

    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)
    print ("Processing session folder: " + sessionFolder)
    
    for sectnum in range(firstsection, lastsection+1):
        print("Processing section: " + str(sectnum))

        #create state table file name
        statetablefile = projectroot + os.path.join("scripts", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum -1 ))

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

            #if os is Linux, convert path
            if platform.system() == 'Linux':
                project_dir = atutils.toPosixPath(projectroot,  "/mnt")
                out_file = atutils.toPosixPath(statetablefile, "/mnt")
            else:
                project_dir = projectroot
                out_file = statetablefile

            #make state table
            #Need to pass posix paths to docker
            cmd = "docker exec " + dockerContainer + " python /pipeline/luigi-scripts/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"%project_dir
            cmd = cmd + " --outputFile %s"%out_file
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
    sessionFolder = os.path.join("/data", "M33", "raw" , "data", "Ribbon0004", "session01")
    dockerContainer = "renderapps_multchan"

    run(sessionFolder, firstsection, lastsection, dockerContainer)
    print ("Finished creation of state tables")
