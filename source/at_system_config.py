import configparser
import os
import ast
import atutils as u
import posixpath
import at_render_project as rp

class ATSystemConfig:
    def __init__(self, iniFile):
        self.config = configparser.ConfigParser()

        #Check that file exists, otherwise raise an error
        if os.path.isfile(iniFile) == False:
            raise Exception("The file: " + iniFile + " don't exist..")

        self.config.read(iniFile)
        self.general                                       = self.config['GENERAL']
        self.deconv                                        = self.config['DECONV']
        self.align                                         = self.config['ALIGN']
        self.tp_client                                     = self.config['TILE_PAIR_CLIENT']
        self.SPARK_SEC                                     = self.config['SPARK']
        self.DATA_INPUT                                    = self.config['DATA_INPUT']

    #The arguments passed here are captured from the commandline and will over ride any option
    #present in the system config file
    def createReferences(self, args = None):
        self.dataRoots                                = ast.literal_eval(self.general['DATA_ROOTS'])
        self.mountRenderPythonApps                    = u.toBool(self.general['MOUNT_RENDER_PYTHON_APPS'])
        self.mountRenderModules                       = u.toBool(self.general['MOUNT_RENDER_MODULES'])
        self.atCoreContainer                          = self.general['AT_CORE_DOCKER_CONTAINER']
        self.atCoreThreads                            = int(self.general['AT_CORE_THREADS'])
        self.downSampleScale                          = self.general['DOWN_SAMPLE_SCALE']

        #
        self.dataOutputFolder                         = self.general['PROCESSED_DATA_FOLDER']

        self.renderHost                               = self.general['RENDER_HOST']
        self.renderHostPort                           = int(self.general['RENDER_HOST_PORT'])
        self.logLevel                                 = self.general['LOG_LEVEL']
        self.clientScripts                            = self.general['CLIENT_SCRIPTS']
        self.memGB                                    = self.general['MEM_GB']

        self.renderProjectOwner                       = self.general['RENDER_PROJECT_OWNER']

        self.referenceChannelRegistration             = self.general['REFERENCE_CHANNEL_REGISTRATION']
        self.JSONTemplatesFolder                      = self.general['JSON_TEMPLATES_FOLDER']

        #JSON Templates
        self.median_template                          = os.path.join(self.JSONTemplatesFolder, "median.json")
        self.stitching_template                       = os.path.join(self.JSONTemplatesFolder, "stitching.json")
        self.flatfield_template                       = os.path.join(self.JSONTemplatesFolder, "flatfield.json")
        self.deconvolution_template                   = os.path.join(self.JSONTemplatesFolder, "deconvolution.json")
        self.alignment_template                       = os.path.join(self.JSONTemplatesFolder, "roughalign.json")
        self.fine_alignment_template                  = os.path.join(self.JSONTemplatesFolder, "fine_align.json")
        self.registrationTemplate                     = os.path.join(self.JSONTemplatesFolder, "registration.json")

        #Deconvolution parameters
        self.channels                                 = ast.literal_eval(self.deconv['CHANNELS'])
        self.bgrdSize                                 = ast.literal_eval(self.deconv['BGRD_SIZE'])
        self.scaleFactor                              = ast.literal_eval(self.deconv['SCALE_FACTOR'])
        self.numIter                                  = int(self.deconv['NUM_ITER'])

        #Alignment parameters
        self.poolSize                                 = int(self.align['POOL_SIZE'])
        self.edgeThreshold                            = int(self.align['EDGE_THRESHOLD'])
        self.scale                                    = float(self.align['SCALE'])
        self.distance                                 = int(self.align['DISTANCE'])
        self.siftMin                                  = float(self.align['SIFTMIN'])
        self.siftMax                                  = float(self.align['SIFTMAX'])
        self.siftSteps                                = int(self.align['SIFTSTEPS'])
        self.renderScale                              = float(self.align['RENDERSCALE'])

        #SPARK stuff
        self.SPARK = {}
        self.SPARK['driverMemory']                    = self.SPARK_SEC['DRIVER_MEMORY']
        self.SPARK['executorMemory']                  = self.SPARK_SEC['EXECUTOR_MEMORY']
        self.SPARK['executorCores']                   = self.SPARK_SEC['EXECUTOR_CORES']
        self.SPARK['maxFeatureCacheGb']               = self.SPARK_SEC['MAX_FEATURE_CACHE_GB']

        self.ch405                                    = self.config['DECONV_405']
        self.ch488                                    = self.config['DECONV_488']
        self.ch594                                    = self.config['DECONV_594']
        self.ch647                                    = self.config['DECONV_647']

        #Tilepair client
        self.excludeCornerNeighbors                   = u.toBool(self.tp_client['EXCLUDE_CORNER_NEIGHBOURS'])
        self.excludeSameSectionNeighbors              = u.toBool(self.tp_client['EXCLUDE_SAME_SECTION_NEIGHBOR'])
        self.zNeighborDistance                        = int(self.tp_client['Z_NEIGHBOR_DISTANCE'])
        self.xyNeighborFactor                         = float(self.tp_client['XY_NEIGHBOR_FACTOR'])

        ##Data input
        self.dataRootFolder                           = self.DATA_INPUT['DATA_ROOT_FOLDER']
        self.projectDataFolder                        = self.DATA_INPUT['PROJECT_DATA_FOLDER']

        #Process parameters
        self.projectName                              = self.DATA_INPUT['PROJECT_NAME']
        self.dataOutputFolder                         = os.path.join(self.projectDataFolder, self.dataOutputFolder, self.projectName)

        self.ribbons                                  = ast.literal_eval(self.DATA_INPUT['RIBBONS'])
        self.sessions                                 = ast.literal_eval(self.DATA_INPUT['SESSIONS'])

        #When used for input data
        #Create a "renderProject"
        self.renderProject = rp.RenderProject(self.renderProjectOwner, self.projectName, self.renderHost, self.renderHostPort, self.clientScripts, self.memGB, self.logLevel)

        if args != None:
            if args.firstsection != None:
                self.firstSection                         = args.firstsection
                self.DATA_INPUT['FIRST_SECTION']          = str(self.firstSection)
            else:
                self.firstSection                         = int(self.DATA_INPUT['FIRST_SECTION'])

            if args.lastsection != None:
                self.lastSection                         = args.lastsection
                self.DATA_INPUT['LAST_SECTION']          = str(self.lastSection)
            else:
                self.lastSection                         = int(self.DATA_INPUT['LAST_SECTION'])

            self.pipeline                                = args.pipeline
            self.overwritedata                           = False #args.overwritedata

    def getStateTableFileName(self, ribbon, session, sectnum):
        return os.path.join(self.dataOutputFolder, "statetables", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum))

    def write(self, fName):
        with open(fName, 'w') as configfile:
            self.config.write(configfile)

    def setupDockerMountName(self, localPath):
        #find the index of localPath in dataRootFolders variable
        mountIndex = 1
        for mount in self.dataRoots:
            if mount == localPath:
                self.dockerMountName = "/data_mount_" + str(mountIndex)
                break
            mountIndex = mountIndex + 1

        if len(self.dockerMountName) == 0:
            raise Exception("The data path: " + localPath + " is not valid")


def toDockerMountedPath2(aPath, paras : ATSystemConfig):
    #Find out index of path in DATA_ROOTS
    index = paras.dataRoots.index(paras.dataRootFolder) + 1

    #Remove rootfolder from aPath
    if aPath.startswith(paras.dataRootFolder):
        aPath = aPath[len(paras.dataRootFolder):]
    else:
        raise ValueError("Bad path in " + __file__)

    aPath = posixpath.normpath(aPath.replace('\\', '/'))
    if aPath[0] == '/':
        aPath = aPath[1:]

    dockerMountName = "/data_mount_" + str(index)
    return posixpath.join(dockerMountName, aPath)
