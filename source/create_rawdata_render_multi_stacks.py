import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)


    renderProjectName = u.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = u.RenderProject("ATExplorer", p.renderHost, renderProjectName)

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
        cmd = cmd + " --render.client_scripts %s" %p.clientScripts
        cmd = cmd + " --render.port 8080"
        cmd = cmd + " --render.memGB 5G"
        cmd = cmd + " --log_level INFO"
        cmd = cmd + " --statetableFile %s"%(u.toDockerMountedPath(statetablefile,  p.prefixPath))
        cmd = cmd + " --projectDirectory %s"%(u.toDockerMountedPath(projectroot,   p.prefixPath))
        cmd = cmd + " --outputStackPrefix ACQ_"

		#Run =============
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
