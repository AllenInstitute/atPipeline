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
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    d_str = "docker exec renderapps_develop "
    render_str = "--render.host %s --render.client_scripts %s --render.port %d --render.memGB %s --log_level %s "%(host,client_scripts,port,memGB,loglevel)
    project_str = "--render.project %s --render.owner %s" %(project, owner)

    cmd_cons = "docker exec "
    cmd_cons = "%s python -m renderapps.stack.consolidate_render_transforms %s %s "%(d_str,render_str,project_str)
    cmd_cons = cmd_cons + "--stack Rough_Aligned_1_DAPI_1 --output_stack Rough_Aligned_1_DAPI_1_CONS --postfix CONS  "
    cmd_cons = cmd_cons + "--output_directory %s/processed/json_tilespecs_consolidation_master --pool_size 20"%project_root_dir

    # Run =============
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

