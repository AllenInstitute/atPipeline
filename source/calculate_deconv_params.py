import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit
import time
def run(p, sessionFolder):

    print ("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject     = u.RenderProject("ATExplorer", p.renderHost, p.projectName)
	
    #RUN python script to calculate scale and background factors for each channel.                     
    cmd = "python deconv_scale_factor_session.py"
    cmd = cmd + "  --drive %s"%(u.toDockerMountedPath(projectroot, p))
    cmd = cmd + " --project %s"%renderProject.name
    cmd = cmd + " --ribbon %s"%ribbon
    cmd = cmd + " --session %s"%session
    cmd = cmd + " --section %s"%p.firstSection

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
