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

    #Output directories
    deconv_dir    = os.path.join("%s"%projectroot, "processed", "deconvolved")

    #Make sure output folder exists
    if os.path.isdir(deconv_dir) == False:
       os.mkdir(deconv_dir)

    #stacks
    ffStack   = "FF_Session%d"%(session)
    dcvStack      = "DCV_Session%d"%(session)

    renderProjectName = u.getProjectNameFromSessionFolder(sessionFolder)
    renderProject     = u.RenderProject("ATExplorer", p.renderHost, renderProjectName)
	
    #Create json files and apply median.
    for sectnum in range(p.firstSection, p.lastSection + 1):

        for i, ch in enumerate(p.channels):

            with open(u.deconvolution_template) as json_data:
                dd = json.load(json_data)

            deconv_json = os.path.join(deconv_dir, "deconvolved""_%s_%s_%s_%d_%s.json"%(renderProject.name, ribbon, session, sectnum, ch))
            psf_dir = os.path.join("%s"%deconv_dir, "psfs")
            psfFile = psf_dir + "psf_%s.tiff"%ch
            z = ribbon*100 + sectnum

            u.savedeconvjson(dd, deconv_json, renderProject.owner, renderProject.name, ffStack, 
                                        dcvStack, u.toDockerMountedPath(deconv_dir, p.prefixPath), z, psfFile, p.numIter, 
                                        p.bgrdSize[i], p.scaleFactor[i], True)
                                        
            cmd = "docker exec " + p.rpaContainer
            cmd = cmd + " python -m renderapps.intensity_correction.apply_deconvolution_multi"
            cmd = cmd + " --render.port 80"
            cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(deconv_json, p.prefixPath))

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