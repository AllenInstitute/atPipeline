import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = atutils.parse_session_folder(sessionFolder)


    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = atutils.RenderProject("ATExplorer", p.renderHost, renderProjectName)

    for sectnum in range(p.firstSection, p.lastSection + 1):
        print("Processing section: " + str(sectnum))

        #State table file
        statetablefile = projectroot + os.path.join("scripts", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum))

        #upload acquisition stacks
        cmd = "docker exec " + p.rpaContainer
        cmd = cmd + " python -m renderapps.dataimport.create_fast_stacks_multi"
        cmd = cmd + " --render.host %s"        %renderProject.host
        cmd = cmd + " --render.owner %s "      %renderProject.owner
        cmd = cmd + " --render.project %s"     %renderProject.name
        cmd = cmd + " --render.client_scripts /shared/render/render-ws-java-client/src/main/scripts"
        cmd = cmd + " --render.port 8080"
        cmd = cmd + " --render.memGB 5G"
        cmd = cmd + " --log_level INFO"
        cmd = cmd + " --statetableFile %s"%(atutils.toDockerMountedPath(statetablefile,  p.prefixPath))
        cmd = cmd + " --projectDirectory %s"%(atutils.toDockerMountedPath(projectroot,   p.prefixPath))
        cmd = cmd + " --outputStackPrefix ACQ_"
        
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