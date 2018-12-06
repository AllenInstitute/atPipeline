#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      matsk
#
# Created:     Oct 24, 2018
#-------------------------------------------------------------------------------

import os
import posixpath
import sys
import json
import platform
import configparser
import ast

#Some hardcoded paths..
templates_folder_mac = "/Users/synbio/ATExplorer/ThirdParty/atPipeline/templates"
templates_folder_win = "c:\\pDisk\\ATExplorer\\ThirdParty\\atPipeline\\templates"
dockerMountName = "/mnt"

if platform.system() == "Windows":
   templates_folder = templates_folder_win
else:
   templates_folder = templates_folder_mac

median_template    = os.path.join(templates_folder, "median.json")
stitching_template = os.path.join(templates_folder, "stitching.json")
flatfield_template = os.path.join(templates_folder, "flatfield.json")
deconvolution_template = os.path.join(templates_folder, "deconvolution.json")
def toBool(v):
  return  v.lower() in ("yes", "true", "t", "1")

class ATDataIni:
      def __init__(self, iniFile):
          config = configparser.ConfigParser()
          config.read(iniFile)
          general= config['GENERAL']
          deconv = config['DECONV']
          align = config['ALIGN']
          self.renderProjectOwner = general['RENDER_PROJECT_OWNER']

          #What data to process??
          self.prefixPath      = general['PREFIX_PATH']
          self.dataRootFolder  = general['DATA_ROOT_FOLDER']
          self.dataRootFolder  = os.path.join(self.prefixPath, self.dataRootFolder)

          #Process parameters
          self.rpaContainer                     = general['RENDER_PYTHON_APPS_CONTAINER']
          self.atmContainer                     = general['AT_MODULES_CONTAINER']
          self.renderHost                       = general['RENDER_HOST']
          self.clientScripts                    = general['CLIENT_SCRIPTS']
          self.port                             = int(general['PORT'])
          self.memGB                            = general['MEM_GB']
          self.logLevel                         = general['LOG_LEVEL']
          self.ribbons                          = ast.literal_eval(general['RIBBONS'])
          self.sessions                         = ast.literal_eval(general['SESSIONS'])
          self.sessionFolders                   = []
          self.firstSection                     = int(general['START_SECTION'])
          self.lastSection                      = int(general['END_SECTION'])
          self.createStateTables                = toBool(general['CREATE_STATE_TABLES'])
          self.createRawDataRenderMultiStacks   = toBool(general['CREATE_RAWDATA_RENDER_MULTI_STACKS'])
          self.createMedianFiles                = toBool(general['CREATE_MEDIAN_FILES'])
          self.createFlatFieldCorrectedData     = toBool(general['CREATE_FLATFIELD_CORRECTED_DATA'])
          self.createStitchedSections           = toBool(general['CREATE_STITCHED_SECTIONS'])
          self.dropStitchingMistakes            = toBool(general['DROP_STITCHING_MISTAKES'])
          self.createLowResStacks               = toBool(general['CREATE_LOWRES_STACKS'])

          #Deconvolution parameters
          self.channels                         = ast.literal_eval(deconv['CHANNELS'])
          self.bgrdSize                         = ast.literal_eval(deconv['BGRD_SIZE'])
          self.scaleFactor                      = ast.literal_eval(deconv['SCALE_FACTOR'])
          self.numIter                          = int(deconv['NUM_ITER'])

          #Alignment parameters
          self.poolSize           = int(align['POOL_SIZE'])
          self.edgeThreshold      = int(align['EDGE_THRESHOLD'])
          self.scale              = float(align['SCALE'])
          self.distance           = int(align['DISTANCE'])
          self.deltaZ             = int(align['DELTAZ'])
          self.minZ               = int(align['MINZ'])
          self.siftMin            = float(align['SIFTMIN'])
          self.siftMax            = float(align['SIFTMAX'])
          self.siftSteps          = int(align['SIFTSTEPS'])
          self.renderScale        = float(align['RENDERSCALE'])


          for session in self.sessions:
              self.sessionFolders.append(os.path.join(self.dataRootFolder, "raw", "data", self.ribbons[0], session))

class RenderProject:
    def __init__(self, owner, host, name):
        self.name = name
        self.host = host
        self.owner = owner

def parse_session_folder(path):
    proj = path.split("raw")
    projectdirectory = proj[0]
    tok = path.split(os.sep)
    ribbondir = tok[len(tok)-2]
    sessiondir = tok[len(tok)-1]
    ribbon = int(ribbondir[6:])
    session = int(sessiondir[7:])
    return [projectdirectory, ribbon, session]

#Input is a sessionfolder path
def getProjectNameFromSessionFolder(sessionFolder):
    print ("Session directory: " + sessionFolder)
    tok = sessionFolder.split(os.sep)
    dataind = tok.index('data')
    print ("Project data folder: " + tok[dataind+1])
    return tok[dataind+1]

def getChannelNamesInSessionFolder(directory):
    directory_list = list()
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in dirs:
            directory_list.append(os.path.join(root, name))
    return dirs

def toDockerMountedPath(path, prefix):
    #Remove prefix
    p = path.split(prefix)[1]
    p = posixpath.normpath(p.replace('\\', '/'))
    return posixpath.join(dockerMountName, p[1:])

def dump_json(data, fileName):
    with open(fileName, 'w') as outfile:
         json.dump(data, outfile, indent=4)

def savemedianjson(template, outFile, render_host, owner, project, acq_stack, median_stack, median_dir, minz, maxz, close_stack):
    template['render']['host']    = render_host
    template['render']['owner']   = owner
    template['render']['project'] = project
    template['input_stack']    = acq_stack
    template['output_stack']      = median_stack
    template['minZ']              = minz
    template['maxZ']              = maxz
    template['output_directory']  = median_dir
    template['close_stack']       = close_stack
    dump_json(template, outFile)

def saveflatfieldjson(template, outFile, render_host, owner, project, acq_stack, median_stack, flatfield_stack, flatfield_dir, sectnum, close_stack):
    template['render']['host']    = render_host
    template['render']['owner']   = owner
    template['render']['project'] = project
    template['input_stack']       = acq_stack
    template['correction_stack']  = median_stack
    template['output_stack']      = flatfield_stack
    template['z_index']           = sectnum
    template['output_directory']  = flatfield_dir
    template['close_stack']       = close_stack
    dump_json(template, outFile)

def savedeconvjson(template,outFile,owner, project, flatfield_stack,deconv_stack,deconv_dir,sectnum,psf_file, num_iter,bgrd_size,scale_factor,close_stack):
    template['render']['owner'] = owner
    template['render']['project'] = project
    template['input_stack'] = flatfield_stack
    template['output_stack'] = deconv_stack
    template['psf_file'] = psf_file
    template['num_iter']=num_iter
    template['bgrd_size'] = bgrd_size
    template['z_index'] = sectnum
    template['output_directory'] = deconv_dir  
    template['scale_factor'] = scale_factor
    template['close_stack'] = close_stack
    dump_json(template, outFile)

def savestitchingjson(template, outfile, owner, project, flatfield_stack, stitched_stack, sectnum, render_host):
    template['owner']                  = owner
    template['project']                = project
    template['stack']                  = flatfield_stack
    template['outputStack']            = stitched_stack
    template['section']                = sectnum
    template['baseDataUrl']            = "http://%s/render-ws/v1"%(render_host)
    dump_json(template, outfile)


def saveroughalignjson(template, outFile, render_host, owner, project, lowres_stack, lowres_pm_collection, roughaligned_stack, client, degree, nfirst, nlast, close_stack):
    template['render']['host']    = render_host
    template['render']['owner']   = owner
    template['render']['project'] = project
    template['input_stack']       = lowres_stack
    template['pointmatch_collection_append1']  = lowres_pm_collection
    template['pointmatch_collection_append2']  = lowres_pm_collection
    template['output_stack']      = roughaligned_stack
    template['degree']           = degree
    template['nfirst']           = nfirst
    template['nlast']           = nlast
    template['client_scripts']  = client
    template['close_stack']       = close_stack
    dump_json(template, outFile)
def main():
    pass

if __name__ == '__main__':
    main()
