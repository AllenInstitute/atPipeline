import os
import time
import json
import sys
import subprocess
import platform
import posixpath
import atutils

def run(sessionFolder, firstsection, lastsection, dockerContainer, renderProject):

    [projectroot, ribbon,session] = atutils.parse_session_folder(sessionFolder)
    print  ("Project root folder: " + projectroot)

    for sectnum in range(firstsection,lastsection+1):
        print("Processing section: " + str(sectnum))

        #create state table
        
        statetablefile = projectroot + os.path.join("scripts", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum -1 ))

        if platform.system() == 'Linux':
                project_dir = atutils.toPosixPath(projectroot,  "/mnt")
                out_file = atutils.toPosixPath(statetablefile, "/mnt")
        #Example
        #docker exec renderapps python -m renderapps.dataimport.create_fast_stacks_multi
        #--render.host localhost
        #--render.client_scripts /shared/render/render-ws-java-client/src/main/scripts
        #--render.port 8080
        #--render.memGB 5G
        #--log_level INFO
        #--statetableFile /data/test
        #--render.project test_project
        #--projectDirectory /data/M33
        #--outputStackPrefix ACQ_Session01
        # --render.owner test

        #upload acquisition stacks
        cmd = "docker exec " + dockerContainer + " python -m renderapps.dataimport.create_fast_stacks_multi"
        cmd = cmd + " --render.host %s"        %renderProject.host
        cmd = cmd + " --render.owner %s "      %renderProject.owner
        cmd = cmd + " --render.project %s"     %renderProject.name
        cmd = cmd + " --render.client_scripts /shared/render/render-ws-java-client/src/main/scripts"
        cmd = cmd + " --render.port 8080"
        cmd = cmd + " --render.memGB 5G"
        cmd = cmd + " --log_level INFO"
        cmd = cmd + " --statetableFile %s"%out_file
        cmd = cmd + " --projectDirectory %s"%project_dir
        cmd = cmd + " --outputStackPrefix ACQ_"
        print ("Running: " + cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print (line)


if __name__ == "__main__":

    firstsection = 1
    lastsection = 24
    sessionFolder = "/Users/synbio/Documents/data/M33/raw/data/Ribbon0004/session01"
    dockerContainer = "renderapps_multchan"
    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", "OSXLTSG3QP.local", renderProjectName)

    run(sessionFolder, firstsection, lastsection, dockerContainer, renderProject)
    print ("done")
