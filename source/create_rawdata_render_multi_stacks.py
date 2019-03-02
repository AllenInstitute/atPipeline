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

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    for sectnum in range(p.firstSection, p.lastSection + 1):
        print("Processing section: " + str(sectnum))

        #State table file
        statetablefile = p.getStateTableFileName(ribbon, session, sectnum)

        #upload acquisition stacks
        cmd = "docker exec " + p.atCoreContainer
        cmd = cmd + " python -m renderapps.dataimport.create_fast_stacks_multi"
        cmd = cmd + " --render.host %s"           %renderProject.host
        cmd = cmd + " --render.owner %s "         %renderProject.owner
        cmd = cmd + " --render.project %s"        %renderProject.name
        cmd = cmd + " --render.client_scripts %s" %p.clientScripts
        cmd = cmd + " --render.port %d"           %p.renderHostPort
        cmd = cmd + " --render.memGB %s"          %p.memGB
        cmd = cmd + " --log_level %s"             %p.logLevel
        cmd = cmd + " --statetableFile %s"        %(posixpath.join(p.dockerDataOutputFolder, "statetables", statetablefile))
        cmd = cmd + " --projectDirectory %s"      %(p.dockerDataInputFolder)
        cmd = cmd + " --dataOutputFolder %s"      %(p.dockerDataOutputFolder)
        cmd = cmd + " --outputStackPrefix S%d_"   %(session)
        cmd = cmd + " --reference_channel %s"      %(p.referenceChannel)

		#Run =============
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
