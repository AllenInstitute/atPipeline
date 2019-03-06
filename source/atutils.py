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

#Some hardcoded paths..
dockerMountName = "/data_mount_1"

def toBool(v):
  return  v.lower() in ("yes", "true", "t", "1")

class ATDataIni:
    def __init__(self, iniFile):
        config = configparser.ConfigParser()
        config.read(iniFile)
        general                                       = config['GENERAL']
        deconv                                        = config['DECONV']
        align                                         = config['ALIGN']
        tp_client                                     = config['TILE_PAIR_CLIENT']
        SPARK_SEC                                     = config['SPARK']

        #What data to process??
        self.prefixPath                               = general['PREFIX_PATH']
        self.dataRootFolder                           = os.path.join(self.prefixPath, general['DATA_FOLDER'])
        self.dataOutputFolder                         = os.path.join(general['PROCESSED_DATA_FOLDER'])

        #Process parameters
        self.atCoreContainer                          = general['RENDER_PYTHON_APPS_CONTAINER']
        self.atmContainer                             = general['AT_MODULES_CONTAINER']
        self.renderHost                               = general['RENDER_HOST']
        self.renderProjectOwner                       = general['RENDER_PROJECT_OWNER']
        self.renderHostPort                           = int(general['RENDER_HOST_PORT'])
        self.projectName                              = general['PROJECT_NAME']

        self.dataOutputFolder                         = os.path.join(  self.dataOutputFolder, self.projectName)
        self.clientScripts                            = general['CLIENT_SCRIPTS']

        self.memGB                                    = general['MEM_GB']
        self.logLevel                                 = general['LOG_LEVEL']
        self.referenceChannel                         = general['REFERENCE_CHANNEL']
        self.ribbons                                  = ast.literal_eval(general['RIBBONS'])
        self.sessions                                 = ast.literal_eval(general['SESSIONS'])
        self.sessionFolders                           = []
        self.firstSection                             = int(general['START_SECTION'])
        self.lastSection                              = int(general['END_SECTION'])
        self.firstRibbon                              = int(general['FIRST_RIBBON'])
        self.lastRibbon                               = int(general['LAST_RIBBON'])
        self.createStateTables                        = toBool(general['CREATE_STATE_TABLES'])
        self.createRawDataRenderMultiStacks           = toBool(general['CREATE_RAWDATA_RENDER_MULTI_STACKS'])
        self.createMedianFiles                        = toBool(general['CREATE_MEDIAN_FILES'])
        self.createFlatFieldCorrectedData             = toBool(general['CREATE_FLATFIELD_CORRECTED_DATA'])
        self.createStitchedSections                   = toBool(general['CREATE_STITCHED_SECTIONS'])
        self.dropStitchingMistakes                    = toBool(general['DROP_STITCHING_MISTAKES'])
        self.createLowResStacks                       = toBool(general['CREATE_LOWRES_STACKS'])
        self.createLRTilePairs                        = toBool(general['CREATE_LOWRES_TILEPAIRS'])
        self.createLRPointMatches                     = toBool(general['CREATE_LOWRES_POINTMATCHES'])
        self.createRoughAlignedStacks                 = toBool(general['CREATE_ROUGH_ALIGNED_STACKS'])
        self.applyLowResToHighRes                     = toBool(general['APPLY_LOWRES_TO_HIGHRES'])
        self.consolidateRoughAlignedStackTransforms   = toBool(general['CONSOLIDATE_ROUGH_ALIGNED_STACK_TRANSFORMS'])
        self.create2DPointMatches                     = toBool(general['CREATE_2D_POINTMATCHES'])
        self.createHRTilePairs                        = toBool(general['CREATE_HR_TILEPAIRS'])
        self.createHRPointMatches                     = toBool(general['CREATE_HR_POINTMATCHES'])
        self.createFineAlignedStacks                  = toBool(general['CREATE_FINE_ALIGNED_STACKS'])


        #SPARK stuff
        self.SPARK = {}
        self.SPARK['driverMemory']                    = SPARK_SEC['DRIVER_MEMORY']
        self.SPARK['executorMemory']                  = SPARK_SEC['EXECUTOR_MEMORY']
        self.SPARK['executorCores']                   = SPARK_SEC['EXECUTOR_CORES']
        self.SPARK['maxFeatureCacheGb']               = SPARK_SEC['MAX_FEATURE_CACHE_GB']


        self.JSONTemplatesFolder                      = general['JSON_TEMPLATES_FOLDER']

        self.ch405                                    = config['DECONV_405']
        self.ch488                                    = config['DECONV_488']
        self.ch594                                    = config['DECONV_594']
        self.ch647                                    = config['DECONV_647']

        #Tilepair client
        self.excludeCornerNeighbors                   = toBool(tp_client['EXCLUDE_CORNER_NEIGHBOURS'])
        self.excludeSameSectionNeighbors              = toBool(tp_client['EXCLUDE_SAME_SECTION_NEIGHBOR'])
        self.zNeighborDistance                        = int(tp_client['Z_NEIGHBOR_DISTANCE'])
        self.xyNeighborFactor                         = float(tp_client['XY_NEIGHBOR_FACTOR'])

        #Deconvolution parameters
        self.channels                                 = ast.literal_eval(deconv['CHANNELS'])
        self.bgrdSize                                 = ast.literal_eval(deconv['BGRD_SIZE'])
        self.scaleFactor                              = ast.literal_eval(deconv['SCALE_FACTOR'])
        self.numIter                                  = int(deconv['NUM_ITER'])

        #Alignment parameters
        self.poolSize                                 = int(align['POOL_SIZE'])
        self.edgeThreshold                            = int(align['EDGE_THRESHOLD'])
        self.scale                                    = float(align['SCALE'])
        self.distance                                 = int(align['DISTANCE'])
        self.siftMin                                  = float(align['SIFTMIN'])
        self.siftMax                                  = float(align['SIFTMAX'])
        self.siftSteps                                = int(align['SIFTSTEPS'])
        self.renderScale                              = float(align['RENDERSCALE'])

        #JSON Templates
        self.median_template                          = os.path.join(self.JSONTemplatesFolder, "median.json")
        self.stitching_template                       = os.path.join(self.JSONTemplatesFolder, "stitching.json")
        self.flatfield_template                       = os.path.join(self.JSONTemplatesFolder, "flatfield.json")
        self.deconvolution_template                   = os.path.join(self.JSONTemplatesFolder, "deconvolution.json")
        self.alignment_template                       = os.path.join(self.JSONTemplatesFolder, "roughalign.json")
        self.fine_alignment_template                  = os.path.join(self.JSONTemplatesFolder, "fine_align.json")
        self.registrationTemplate                     = os.path.join(self.JSONTemplatesFolder, "registration.json")

        for session in self.sessions:
          self.sessionFolders.append(os.path.join(self.dataRootFolder, "raw", "data", self.ribbons[0], session))

    def getStateTableFileName(self, ribbon, session, sectnum):
        return os.path.join(self.dataRootFolder, self.dataOutputFolder, "statetables", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum))


def validateATCoreInputAndOutput():
    parser = argparse.ArgumentParser()
    parser.add_argument('parameter_file', help='Input file')
    args = parser.parse_args()
    parameterFile = args.parameter_file

    #Check that input file exists, if not bail
    if os.path.isfile(parameterFile) == False:
        raise ValueError("The input file: " + parameterFile + " don't exist. Bailing..")

    parameters = ATDataIni(parameterFile)

    #Copy parameter file to root of processed data output folder
    outFolder = os.path.join(parameters.dataRootFolder, parameters.dataOutputFolder)
    if os.path.isdir(outFolder) == False:
        pathlib.Path(outFolder).mkdir(parents=True, exist_ok=True)

    shutil.copy2(parameterFile, outFolder)
    return parameters


def runAtCoreModule(method):
    timeStart = timeit.default_timer()
    parameters =validateATCoreInputAndOutput()

    for sessionFolder in parameters.sessionFolders:
        method(parameters, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")

class RenderProject:
    def __init__(self, owner, host, name, host_port="80", client_scripts="/shared/render/render-ws-java-client/src/main/scripts"):
        self.name           = name
        self.host           = host
        self.owner          = owner
        self.hostPort       = host_port
        self.clientScripts  = client_scripts

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

def savemedianjson(template, outFile, render_project, acq_stack, median_stack, median_dir, minz, maxz, close_stack):
    template['render']['host']    = render_project.host
    template['render']['owner']   = render_project.owner
    template['render']['project'] = render_project.name
    template['input_stack']       = acq_stack
    template['output_stack']      = median_stack
    template['minZ']              = minz
    template['maxZ']              = maxz
    template['output_directory']  = median_dir
    template['close_stack']       = close_stack
    dump_json(template, outFile)

def saveflatfieldjson(template, outFile, render_project, acq_stack, median_stack, flatfield_stack, flatfield_dir, sectnum, close_stack):
    template['render']['host']    = render_project.host
    template['render']['owner']   = render_project.owner
    template['render']['project'] = render_project.name
    template['input_stack']       = acq_stack
    template['correction_stack']  = median_stack
    template['output_stack']      = flatfield_stack
    template['z_index']           = sectnum
    template['output_directory']  = flatfield_dir
    template['close_stack']       = close_stack
    dump_json(template, outFile)

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

def savestitchingjson(template, outfile, render_project, flatfield_stack, stitched_stack, sectnum):
    template['baseDataUrl']            = "http://%s/render-ws/v1"%(render_project.host)
    template['owner']                  = render_project.owner
    template['project']                = render_project.name
    template['stack']                  = flatfield_stack
    template['outputStack']            = stitched_stack
    template['section']                = sectnum
    dump_json(template, outfile)

def saveRoughAlignJSON(template, outFile, renderProject, input_stack, output_stack, lowresPmCollection, logLevel, nFirst, nLast, dataOutputFolder):
    template['regularization']['log_level']                  = logLevel
    template['matrix_assembly']['log_level']                 = logLevel

    template['output_stack']['client_scripts']               = renderProject.clientScripts
    template['output_stack']['owner']                        = renderProject.owner
    template['output_stack']['log_level']                    = logLevel
    template['output_stack']['project']                      = renderProject.name
    template['output_stack']['port']                         = renderProject.hostPort
    template['output_stack']['host']                         = renderProject.host
    template['output_stack']['name']                         = output_stack

    template['input_stack']['client_scripts']                = renderProject.clientScripts
    template['input_stack']['owner']                         = renderProject.name
    template['input_stack']['log_level']                     = logLevel
    template['input_stack']['project']                       = renderProject.name
    template['input_stack']['port']                          = renderProject.hostPort
    template['input_stack']['host']                          = renderProject.host
    template['input_stack']['name']                          = input_stack

    template['pointmatch']['client_scripts']                 = renderProject.clientScripts
    template['pointmatch']['owner']                          = renderProject.owner
    template['pointmatch']['log_level']                      = logLevel
    template['pointmatch']['project']                        = renderProject.name
    template['pointmatch']['name']                           = lowresPmCollection
    template['pointmatch']['port']                           = renderProject.hostPort
    template['pointmatch']['host']                           = renderProject.host

    template['hdf5_options']['log_level']                    = logLevel
    template['hdf5_options']['output_dir']                   = dataOutputFolder

    template['first_section']                                = nFirst
    template['last_section']                                 = nLast
    template['log_level']                                    = "INFO"
    dump_json(template, outFile)

def saveFineAlignJSON(template, outFile, renderHost, port, owner, project, input_stack, output_stack, collection_2D, collection_3D, clientScripts, logLevel, nFirst, nLast, dataOutputFolder):
    template['regularization']['log_level']                  = logLevel
    template['matrix_assembly']['log_level']                 = logLevel

    template['output_stack']['client_scripts']               = clientScripts
    template['output_stack']['owner']                        = owner
    template['output_stack']['log_level']                    = logLevel
    template['output_stack']['project']                      = project
    template['output_stack']['name']                         = output_stack
    template['output_stack']['port']                         = port
    template['output_stack']['host']                         = renderHost

    template['input_stack']['client_scripts']                = clientScripts
    template['input_stack']['owner']                         = owner
    template['input_stack']['log_level']                     = logLevel
    template['input_stack']['project']                       = project
    template['input_stack']['port']                          = port
    template['input_stack']['host']                          = renderHost
    template['input_stack']['name']                          = input_stack

    template['pointmatch']['client_scripts']                 = clientScripts
    template['pointmatch']['owner']                          = owner
    template['pointmatch']['log_level']                      = logLevel
    template['pointmatch']['project']                        = project
    template['pointmatch']['name']                           = [collection_2D, collection_3D]
    template['pointmatch']['port']                           = port
    template['pointmatch']['host']                           = renderHost

    template['hdf5_options']['log_level']                    = logLevel
    template['hdf5_options']['output_dir']                   = dataOutputFolder

    template['last_section']                                 = nLast
    template['first_section']                                = nFirst
    template['log_level']                                    = "INFO"
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
