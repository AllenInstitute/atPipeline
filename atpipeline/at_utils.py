import os
import posixpath
import sys
import json
import platform
import configparser
import ast
import argparse
import shutil
import timeit
import pathlib
import subprocess
import logging
from . import at_system_config
logger = logging.getLogger('atPipeline')

def toBool(v):
  return  v.lower() in ("yes", "true", "t", "1")

def setupParameters():
    parser = argparse.ArgumentParser()
    parser.add_argument('parameter_file', help='Input file')
    args = parser.parse_args()
    parameterFile = args.parameter_file

    #Check that input file exists, if not bail
    if os.path.isfile(parameterFile) == False:
        raise ValueError("The input file: " + parameterFile + " don't exist. Bailing..")

    parameters = ATDataIni(parameterFile)

    #Copy parameter file to root of processed data output folder
    outFolder = os.path.join(parameters.projectRootFolder, parameters.dataOutputFolder)
    if os.path.isdir(outFolder) == False:
        pathlib.Path(outFolder).mkdir(parents=True, exist_ok=True)

    shutil.copy2(parameterFile, outFolder)
    return parameters

def runAtCoreModule(method, logger):
    timeStart = timeit.default_timer()
    parameters = setupParameters()

    for sessionFolder in parameters.sessionFolders:
        method(parameters, sessionFolder, logger)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    logger.info("Elapsed time: " + timeDuration + " minutes")

def getJSON(cmd):
    logger.info("===================== Running: " + cmd.replace('--', '\n--') + "\n---------------------------------------")
    proc = None
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    result = proc.communicate()[0]

    if proc.returncode:
        logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("Error Running Command: " + cmd)

    return result

def runShellCMD(cmd, logs = True):
    logger.debug("===================== Running: " + cmd.replace('--', '\n--') + "\n---------------------------------------")
    #proc = None
    useShell = True
    if logs:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=useShell, stderr=subprocess.STDOUT, encoding='utf-8')
    else:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=useShell, encoding='utf-8')

    lines = []
    for line in proc.stdout.readlines():
        logger.debug(line.rstrip())
        lines.append(line)

    proc.wait()
    if proc.returncode:
        logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("Error Running Command: " + cmd)
    return lines

def runPipelineStep(cmd, stepName):
    logger.info("===================== Running Pipeline Step: " + stepName + cmd.replace('--', '\n--') + "\n---------------------------------------")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
    for line in proc.stdout.readlines():
        logger.debug(line.rstrip())

    proc.wait()
    if proc.returncode:
        logger.error("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception("Error in pipeline step: " + stepName)

#Move this to render_classes folder
class RenderProject:
    def __init__(self, owner, project_name, host_name, host_port, client_scripts, mem_gb, log_level):
        self.owner          = owner
        self.project_name    = project_name
        self.host           = host_name
        self.hostPort       = host_port
        self.clientScripts  = client_scripts
        self.memGB          = mem_gb
        self.logLevel       = log_level

def get_number_of_physical_tiles_in_section(sectnum:int, current_ribbon, data_info):
    #Get sectiondata from data_info dictionary
    ribbon_id = get_ribbon_id_from_ribbon_folder_name(current_ribbon, data_info)
    nr_of_channels = data_info["atdata"]["TotalNumberOfChannels"]
    ribbons = data_info["atdata"]["Ribbons"]
    section = ribbons[ribbon_id]["Sections"][sectnum]
    nr_of_tiles = section["NumberOfTiles"]

    #Divide by number of channels
    return nr_of_tiles / nr_of_channels

def get_ribbon_id_from_ribbon_folder_name(ribbon_folder, data_info):

    ribbons = data_info["atdata"]["RibbonFolders"]
    return ribbons.index(ribbon_folder)

def parse_session_folder(path):
    proj = path.split("raw")
    projectdirectory = proj[0]
    tok = path.split(os.sep)
    ribbondir = tok[len(tok)-2]
    sessiondir = tok[len(tok)-1]
    ribbon = int(ribbondir[6:])
    session = int(sessiondir[7:])
    return [projectdirectory, ribbon, session]

def getRibbonLabelFromSessionFolder(path):
    proj = path.split("raw")
    tok = path.split(os.sep)
    ribbondir = tok[len(tok)-2]
    return ribbondir

#Input is a sessionfolder path
def getProjectNameFromSessionFolder(sessionFolder):
    logger.info("Session directory: " + sessionFolder)
    tok = sessionFolder.split(os.sep)
    dataind = tok.index('data')
    logger.info("Project data folder: " + tok[dataind+1])
    return tok[dataind+1]

def getChannelNamesInSessionFolder(directory):
    directory_list = list()
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in dirs:
            directory_list.append(os.path.join(root, name))
    return dirs

def dump_json(data, fileName):
    with open(fileName, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def savedeconvjson(template,outFile, owner, project, flatfield_stack,deconv_stack,deconv_dir,sectnum,psf_file, num_iter,bgrd_size,scale_factor,close_stack):
    template['render']['owner']   = owner
    template['render']['project'] = project
    template['input_stack']       = flatfield_stack
    template['output_stack']      = deconv_stack
    template['psf_file']          = psf_file
    template['num_iter']          = num_iter
    template['bgrd_size']         = bgrd_size
    template['z_index']           = sectnum
    template['output_directory']  = deconv_dir
    template['scale_factor']      = scale_factor
    template['close_stack']       = close_stack
    dump_json(template, outFile)

def saveRegistrationJSON(t, outFileName, renderHost, owner, project, stack, referenceStack, outputStack, section):
    t['baseDataUrl']                                         = "http://%s/render-ws/v1"%(renderHost)
    t['owner']                                               = owner
    t['project']                                             = project
    t['stack']                                               = stack
    t['referencestack']                                      = referenceStack
    t['outputStack']                                         = outputStack
    t['section']                                             = section
    t['steps']                                               = 5
    t['maxEpsilon']                                          = 2
    t['minOctaveSize']                                       = 1000
    t['maxOctaveSize']                                       = 2000
    t['initialSigma']                                        = 2.5
    t['percentSaturated']                                    = 0.9
    t['contrastEnhance']                                     = False

    #Write the JSON
    dump_json(t, outFileName)

def main():
    pass

if __name__ == '__main__':
    main()
