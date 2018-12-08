import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit


def run(p, sessionFolder):

	print ("Processing session folder: " + sessionFolder)
	[projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

	# output directories
	downsample_dir = "%s/processed/Low_res"%(projectRoot)
	pm_script_dir = "/pipeline/sharmi/Sharmi_tools/render-branches/from_fcollman/render/render-ws-spark-client/src/main/scripts"
	numsections_file = "%s/numsections"%downsample_dir

	# stacks
	lowres_stack = "LR_DRP_STI_Session%d"%(session)

	renderProjectName = u.getProjectNameFromSessionFolder(sessionFolder)
	renderProject = u.RenderProject("ATExplorer", p.renderHost, renderProjectName)

	#point match collections
	lowres_pm_collection = "%s_Lowres_3D"%renderProject.name

	#get numsections
	f = open(numsections_file)
	numSections = int(f.readline())
	print numSections

	# docker commands
	#Extract point matches
	cmd = "docker exec " + p.rpaContainer
	cmd = cmd + " sh %s/run_tilepair_and_sift.sh"%pm_script_dir
	cmd = cmd + " --render.port %s"%p.port
	cmd = cmd + " --render.host %s"%renderProject.host
	cmd = cmd + " --render.client_scripts %s"%p.clientScripts
	cmd = cmd + " --render.memGB %s"%p.memGB
	cmd = cmd + " --render.log_level %s"%p.logLevel
	cmd = cmd + " --render.project %s"%renderProject.name
	cmd = cmd + " --render.owner %s"%renderProject.owner
	cmd = cmd + " --stack %s"%lowres_stack
	cmd = cmd + " --collection %s"%lowres_pm_collection
	cmd = cmd + " --minZ 0"
	cmd = cmd + " --maxZ %d"%numSections
	cmd = cmd + " --deltaZ %s"%p.deltaZ
	cmd = cmd + " --renderScale %s"%p.renderScale
	cmd = cmd + " --SIFTminScale %s"%p.siftMin
	cmd = cmd + " --SIFTmaxScale %s"%p.siftMax
	cmd = cmd + " --SIFTsteps %s"%p.siftSteps



	# Run =============
	print ("Running: " + cmd)

	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for i in range(0,2):	
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

