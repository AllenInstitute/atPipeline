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

	# output directories
	dropped_dir = "%s/processed/dropped" %(projectRoot)

	# Make sure output folder exist
	if os.path.isdir(dropped_dir) == False:
		os.mkdir(dropped_dir)

	# stacks
	acquisition_Stack = "ACQ_Session%d" % (session)
	stitched_dapi_Stack = "STI_Session%d" % (session)
	dropped_dapi_Stack = "DRP_STI_Session%d" % (session)

	renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolder)
	renderProject = atutils.RenderProject("ATExplorer", p.renderHost, renderProjectName)

	# docker strings
	d_str = "docker exec %s"%p.rpaContainer
	render_str = "--render.host %s --render.client_scripts %s --render.port %d --render.memGB %s --log_level %s "%(renderProject.host,p.clientScripts,p.port,p.memGB,p.logLevel)
	project_str = "--render.project %s --render.owner %s" %(renderProject.name, renderProject.owner)
	output_str = "--prestitchedStack %s --poststitchedStack %s --outputStack %s --jsonDirectory %s"%(acquisition_Stack,stitched_dapi_Stack,dropped_dapi_Stack,dropped_dir)
	params_str = "--edge_threshold %d --pool_size %d --distance_threshold %d"%(p.edgeThreshold,p.poolSize,p.distance)

	# docker commands
	cmd = "%s python -m renderapps.stitching.detect_and_drop_stitching_mistakes %s %s %s %s"%(d_str,render_str, project_str, output_str, params_str)

	# Run =============
	print ("Running: " + cmd)

	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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

