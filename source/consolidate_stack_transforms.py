##Create new
import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit

##Create a new stack with "consolidated" transforms
def run(p, sessionFolder):
    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)

    cmd = "docker exec "+ p.atCoreContainer
    cmd = cmd + " python -m rendermodules.stack.consolidate_transforms"
    cmd = cmd + " --render.host %s"                           %(renderProject.host)
    cmd = cmd + " --render.project %s"                        %(renderProject.name)
    cmd = cmd + " --render.owner %s"                          %(renderProject.owner)
    cmd = cmd + " --render.client_scripts %s"                 %(p.clientScripts)
    cmd = cmd + " --render.memGB %s"                          %(p.memGB)
    cmd = cmd + " --render.port %s"                           %(p.port)
    cmd = cmd + " --pool_size %s"                             %(p.poolSize)
    cmd = cmd + " --stack S%d_RoughAligned"                        %(session)
    cmd = cmd + " --output_stack S%d_RoughAligned_Consolidated"    %(session)
    cmd = cmd + " --close_stack %d"%(True)
    cmd = cmd + " --output_json Test"

    # Run =============
    print ("Running: " + cmd.replace('--', '\n--'))

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
    	print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("consolidate_stack_transforms threw an Exception")


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)


