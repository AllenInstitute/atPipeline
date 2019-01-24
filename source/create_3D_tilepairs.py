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

    #3D point matches
    mychannel = "DAPI_1"

    beg_indices = [30]
    end_indices = [57]

    for i in range(0, len(beg_indices)):
    	minZ = beg_indices[i]
    	maxZ = end_indices[i]
    	json_file = "/nas4/data/%s/processed/tilepairfiles1/tilepairs-10-%d-%d-nostitch-EDIT.json"%(project,minZ,maxZ)
    	cmd_ex1 = "%s/run_tilepair_only.sh --owner %s --project %s --stack Rough_Aligned_1_DAPI_1_CONS --minZ %d --maxZ  %d --collection %s_%s --deltaZ 10 --renderWithFilter true --jsonFile %s"%(pm_script_dir,owner,project,minZ,maxZ,highres_pm_collection,mychannel,json_file)
    	cmd_ex2 = "%s/run_sift_on_tilepair_client.sh --owner %s --project %s --stack Rough_Aligned_1_DAPI_1_CONS --minZ %d --maxZ %d --collection %s_%s --deltaZ 10  --jsonFile %s --renderWithFilter true --siftsteps 3 --renderScale .3 --SIFTminScale .6 --SIFTmaxScale .7 --mininliers 8"%(pm_script_dir,owner,project,minZ, maxZ, highres_pm_collection,mychannel,json_file)
    	print json_file
    	print cmd_ex1
    	print cmd_ex2
    	os.system(cmd_ex1)
    	os.system(cmd_ex2)

    cmd_cons = "docker exec "

    # Run =============
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

