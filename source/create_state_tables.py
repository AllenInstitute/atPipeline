import os
import subprocess
import atutils as u
import posixpath

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    for sectnum in range(p.firstSection, p.lastSection + 1):
        print("Processing section: " + str(sectnum))

        #State table file
        statetablefile = p.getStateTableFileName(ribbon, session, sectnum)
        print("Creating statetable file: " + statetablefile)

        if os.path.exists(os.path.join(p.dataOutputFolder, 'statetables' , statetablefile)):
           print("The statetable: " + statetablefile + " already exists in folder " + os.path.join(p.dataOutputFolder, 'statetables' ) + ". Continuing..")
        else:
            cmd = "docker exec " + p.atCoreContainer
            cmd = cmd + " python /pipeline/make_state_table_ext_multi_pseudoz.py"
            cmd = cmd + " --projectDirectory %s"        %(u.toDockerMountedPath(p.dockerDataInputRootFolder, p.projectName))
            cmd = cmd + " --outputFile %s"              %(posixpath.join(p.dockerDataOutputFolder, 'statetables', statetablefile))
            cmd = cmd + " --ribbon %d"                  %ribbon
            cmd = cmd + " --session %d"                 %session
            cmd = cmd + " --section %d"                 %(sectnum)
            cmd = cmd + " --oneribbononly True"

		    #Run ====================
            print ("Running: " + cmd.replace('--', '\n--'))

            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout.readlines():
                print (line)

            proc.wait()
            if proc.returncode:
                print ("PROC_RETURN_CODE:" + str(proc.returncode))
                raise Exception("Error generating median files")

if __name__ == "__main__":
    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
