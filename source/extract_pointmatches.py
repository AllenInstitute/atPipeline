import os
import json
import sys
import subprocess
import posixpath
import atutils
import timeit


def run(p, sessionFolder):

	print ("Processing session folder: " + sessionFolder)
	[projectRoot, ribbon, session] = atutils.parse_session_folder(sessionFolder)
	firstRibbon = ribbon
	lastRibbon = int(p.ribbons[-1][6:])

	# output directories
	pm_script_dir = "/pipeline/sharmi/Sharmi_tools/render-branches/from_fcollman/render/render-ws-spark-client/src/main/scripts"
	numsections_file = "%s/numsections"%downsample_dir

	# Make sure output folder exist 
	if os.path.isdir(downsample_dir) == False:
		os.mkdir(downsample_dir)

	# stacks
	lowres_stack = "LR_DRP_STI_Session%d"%(session)

	renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
	renderProject = atutils.RenderProject("ATExplorer", p.renderHost, renderProjectName)

	# docker commands
	#Extract point matches
	##cmd_pointmatches = "sh %s/run_tilepair_and_sift.sh --owner %s --project %s --stack %s --minZ 0 --maxZ %d --collection %s --deltaZ %d"%(pm_script_dir,owner,project,lowres_stack, 2090, lowres_pm_collection,deltaZ)
	cmd = " --stack %s --minZ 0 --maxZ %d --collection %s --deltaZ %d"%(lowres_stack,numberofsections,lowres_pm_collection,deltaZ)
	cmd = cmd + " --renderScale 1.0 --SIFTminScale 0.6 --SIFTmaxScale 1.0 --SIFTsteps 3"

	cmd = "docker exec " + p.rpaContainer
	cmd = cmd + " sh %s/run_tilepair_and_sift.sh"%(atutils.toDockerMountedPath(pm_script_dir, p.prefixPath))
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
	cmd = cmd + " --maxZ %d"%numberofsections
	cmd = cmd + " --deltaZ %s"%deltaZ
	cmd = cmd + " --renderScale %s"%p.renderScale
	cmd = cmd + " --SIFTminScale %s"%p.SIFTminScale
	cmd = cmd + " --SIFTmaxScale %s"%p.SIFTmaxScale
	cmd = cmd + " --SIFTsteps %s"%p.SIFTsteps



	# Run =============
	print ("Running: " + cmd)

	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for i in range(0,2):	
		for line in proc.stdout.readlines():
			print (line)


if __name__ == "__main__":
    timeStart = timeit.default_timer()
    f = os.path.join('..', 'ATData_params.ini')
    p = atutils.ATDataIni(f)

    for sessionFolder in p.sessionFolders:
        run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")

