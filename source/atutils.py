import os
import posixpath
import sys
import json
import platform
import configparser
import ast

#Some hardcoded paths..
dockerMountName = "/mnt"

templates_folder = "templates"
median_template        = os.path.join("..", templates_folder, "median.json")
stitching_template     = os.path.join("..", templates_folder, "stitching.json")
flatfield_template     = os.path.join("..", templates_folder, "flatfield.json")
deconvolution_template = os.path.join("..", templates_folder, "deconvolution.json")
alignment_template     = os.path.join("..", templates_folder, "roughalign.json")

def toBool(v):
  return  v.lower() in ("yes", "true", "t", "1")

class ATDataIni:
      def __init__(self, iniFile):
          config = configparser.ConfigParser()
          config.read(iniFile)
          general                               = config['GENERAL']
          deconv                                = config['DECONV']
          align                                 = config['ALIGN']
          tp_client                             = config['TILE_PAIR_CLIENT']

          self.ch405                            = config['DECONV_405']
          self.ch488                            = config['DECONV_488']
          self.ch594                            = config['DECONV_594']
          self.ch647                            = config['DECONV_647']

          #What data to process??
          self.prefixPath                       = general['PREFIX_PATH']
          self.dataRootFolder                   = os.path.join(self.prefixPath, general['DATA_FOLDER'])
          self.dataOutputFolder                 = os.path.join(general['PROCESSED_DATA_FOLDER'])

          #Process parameters
          self.rpaContainer                     = general['RENDER_PYTHON_APPS_CONTAINER']
          self.atmContainer                     = general['AT_MODULES_CONTAINER']
          self.renderHost                       = general['RENDER_HOST']
          self.renderProjectOwner               = general['RENDER_PROJECT_OWNER']
          self.renderProjectName                = general['RENDER_PROJECT_NAME']
          self.clientScripts                    = general['CLIENT_SCRIPTS']
          self.port                             = int(general['PORT'])
          self.memGB                            = general['MEM_GB']
          self.logLevel                         = general['LOG_LEVEL']
          self.ribbons                          = ast.literal_eval(general['RIBBONS'])
          self.sessions                         = ast.literal_eval(general['SESSIONS'])
          self.sessionFolders                   = []
          self.firstSection                     = int(general['START_SECTION'])
          self.lastSection                      = int(general['END_SECTION'])
          self.firstRibbon                      = int(general['FIRST_RIBBON'])
          self.lastRibbon                       = int(general['LAST_RIBBON'])
          self.createStateTables                = toBool(general['CREATE_STATE_TABLES'])
          self.createRawDataRenderMultiStacks   = toBool(general['CREATE_RAWDATA_RENDER_MULTI_STACKS'])
          self.createMedianFiles                = toBool(general['CREATE_MEDIAN_FILES'])
          self.createFlatFieldCorrectedData     = toBool(general['CREATE_FLATFIELD_CORRECTED_DATA'])
          self.createStitchedSections           = toBool(general['CREATE_STITCHED_SECTIONS'])
          self.dropStitchingMistakes            = toBool(general['DROP_STITCHING_MISTAKES'])
          self.createLowResStacks               = toBool(general['CREATE_LOWRES_STACKS'])
          self.createTilePairs                  = toBool(general['CREATE_TILE_PAIRS'])
          self.createPointMatches               = toBool(general['CREATE_POINT_MATCHES'])
          self.createRoughAlignedStacks         = toBool(general['CREATE_ROUGH_ALIGNED_STACKS'])

          #Tilepair client
          self.excludeCornerNeighbors           = toBool(tp_client['EXCLUDE_CORNER_NEIGHBOURS'])
          self.excludeSameSectionNeighbors      = toBool(tp_client['EXCLUDE_SAME_SECTION_NEIGHBOR'])
          self.zNeighborDistance                = int(tp_client['Z_NEIGHBOR_DISTANCE'])
          self.xyNeighborFactor                 = float(tp_client['XY_NEIGHBOR_FACTOR'])

          #Deconvolution parameters
          self.channels                         = ast.literal_eval(deconv['CHANNELS'])
          self.bgrdSize                         = ast.literal_eval(deconv['BGRD_SIZE'])
          self.scaleFactor                      = ast.literal_eval(deconv['SCALE_FACTOR'])
          self.numIter                          = int(deconv['NUM_ITER'])

          #Alignment parameters
          self.poolSize                         = int(align['POOL_SIZE'])
          self.edgeThreshold                    = int(align['EDGE_THRESHOLD'])
          self.scale                            = float(align['SCALE'])
          self.distance                         = int(align['DISTANCE'])
          self.siftMin                          = float(align['SIFTMIN'])
          self.siftMax                          = float(align['SIFTMAX'])
          self.siftSteps                        = int(align['SIFTSTEPS'])
          self.renderScale                      = float(align['RENDERSCALE'])

          for session in self.sessions:
              self.sessionFolders.append(os.path.join(self.dataRootFolder, "raw", "data", self.ribbons[0], session))

      def getStateTableFileName(self, ribbon, session, sectnum):
          return os.path.join(self.dataRootFolder, self.dataOutputFolder, "statetables", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum))


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
    template['input_stack']       = acq_stack
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

def savestitchingjson(template, outfile, owner, project, flatfield_stack, stitched_stack, sectnum, render_host):
    template['owner']                  = owner
    template['project']                = project
    template['stack']                  = flatfield_stack
    template['outputStack']            = stitched_stack
    template['section']                = sectnum
    template['baseDataUrl']            = "http://%s/render-ws/v1"%(render_host)
    dump_json(template, outfile)

def saveroughalignjson(template, outFile, renderHost, port, owner, project, lowresStack, lowresPmCollection, roughalignedStack, clientScripts, logLevel, nFirst, nLast, dataOutputFolder):
    template['regularization']['log_level']                  = logLevel
    template['matrix_assembly']['log_level']                 = logLevel

    template['output_stack']['client_scripts']               = clientScripts
    template['output_stack']['owner']                        = owner
    template['output_stack']['log_level']                    = logLevel
    template['output_stack']['project']                      = project
    template['output_stack']['name']                         = roughalignedStack
    template['output_stack']['port']                         = port
    template['output_stack']['host']                         = renderHost

    template['input_stack']['client_scripts']                = clientScripts
    template['input_stack']['owner']                         = owner
    template['input_stack']['log_level']                     = logLevel
    template['input_stack']['project']                       = project
    template['input_stack']['port']                          = port
    template['input_stack']['host']                          = renderHost

    template['pointmatch']['client_scripts']                 = clientScripts
    template['pointmatch']['owner']                          = owner
    template['pointmatch']['log_level']                      = logLevel
    template['pointmatch']['project']                        = project
    template['pointmatch']['name']                           = lowresPmCollection
    template['pointmatch']['port']                           = port
    template['pointmatch']['host']                           = renderHost

    template['hdf5_options']['log_level']                    = logLevel
    template['hdf5_options']['output_dir']                   = dataOutputFolder

    template['last_section']                                 = nLast
    template['first_section']                                = nFirst
    template['log_level']                                    = "INFO"
    dump_json(template, outFile)

def main():
    pass

if __name__ == '__main__':
    main()
