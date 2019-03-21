import os
import json
import sys
import subprocess
import posixpath
import atutils as u
import timeit
import time
import csv
import logging

logger = logging.getLogger('atPipeline')

def set_channel_dict(file_dir, channel):

    with open(file_dir) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

    channel_dir = {
            'chNum' =
            'chName'=
            'bgScale' =
            'scaleFactor' =
            }

def run(p : u.ATDataIni, sessionFolder):

    logger.info("Processing session folder: " + sessionFolder)
    [projectroot, ribbon, session] = u.parse_session_folder(sessionFolder)

    #Directories
    deconv_params_dir = os.path.join(projectroot,'processed','deconv_scale_factors')
    deconv_dir    = os.path.join("%s"%projectroot, "processed", "deconvolved")

    #Make sure output folder exists
    if os.path.isdir(deconv_dir) == False:
       os.mkdir(deconv_dir)

    #stacks
    ffStack   = "S%d_FlatFielded"%(session)
    dcvStack  = "S%d_Deconvolved"%(session)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.projectName, p.sys.renderHost)

    channels = [p.ch405,p.ch488,p.ch594,p.ch647]
    #Create json files and apply median.
    for sectnum in range(p.firstSection, p.lastSection + 1):

        for ch in channels:
            if ch["LABEL"] != None:
                with open(p.systemParameters.deconvolution_template) as json_data:
                    dd = json.load(json_data)

                deconv_json = os.path.join(deconv_dir, "deconvolved""_%s_%s_%s_%d_%s.json"%(renderProject.projectName, ribbon, session, sectnum, ch["LABEL"]))
                psf_dir = os.path.join("%s"%deconv_dir, "psfs")
                psfFile = psf_dir + "psf_%s.tiff"%ch["CHANNEL"]
                z = ribbon*100 + sectnum

                u.savedeconvjson(dd, deconv_json, renderProject.owner, renderProject.projectName, ffStack,
                                            dcvStack, u.toDockerMountedPath(deconv_dir, p), z, psfFile, ch["NUM_ITER"],
                                            ch["BGRD_SIZE"], ch["SCALE_FACTOR"], True)

                cmd = "docker exec " + p.sys.atCoreContainer
                cmd = cmd + " python -m renderapps.intensity_correction.apply_deconvolution_multi"
                cmd = cmd + " --render.port 80"
                cmd = cmd + " --input_json %s"%(u.toDockerMountedPath(deconv_json, p))

            #Run =============
    		u.runPipelineStep(cmd, __file__)


if __name__ == "__main__":

    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)