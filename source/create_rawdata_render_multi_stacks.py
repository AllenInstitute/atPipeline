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

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.renderProjectName)

    for sectnum in range(p.firstSection, p.lastSection + 1):
        print("Processing section: " + str(sectnum))

        #State table file
        statetablefile = p.getStateTableFileName(ribbon, session, sectnum)

        #upload acquisition stacks
        cmd = "docker exec " + p.rpaContainer
        cmd = cmd + " python -m renderapps.dataimport.create_fast_stacks_multi"
        cmd = cmd + " --render.host %s"           %renderProject.host
        cmd = cmd + " --render.owner %s "         %renderProject.owner
        cmd = cmd + " --render.project %s"        %renderProject.name
        cmd = cmd + " --render.client_scripts %s" %p.clientScripts
        cmd = cmd + " --render.port %d"           %p.port
        cmd = cmd + " --render.memGB %s"          %p.memGB
        cmd = cmd + " --log_level %s"             %p.logLevel
        cmd = cmd + " --statetableFile %s"        %(u.toDockerMountedPath(statetablefile,  p.prefixPath))
        cmd = cmd + " --projectDirectory %s"      %(u.toDockerMountedPath(projectroot,   p.prefixPath))
        cmd = cmd + " --dataOutputFolder %s"      %(p.dataOutputFolder.replace('\\', '/'))
        cmd = cmd + " --outputStackPrefix ACQ_"
        cmd = cmd + " --reference_channel %s"      %(p.referenceChannel)

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
