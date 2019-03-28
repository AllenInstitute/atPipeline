import configparser
import os
import ast
import at_utils as u
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
        self.mounts                                        = ast.literal_eval(self.general['DATA_ROOTS'])

    #The arguments passed here are captured from the commandline and will over ride any option
    #present in the system config file
    def createReferences(self, args = None, caller = None, dataInfo = None):

        self.atCoreContainer                          = self.general['AT_CORE_DOCKER_CONTAINER']
        self.atCoreThreads                            = int(self.general['AT_CORE_THREADS'])
        self.downSampleScale                          = self.general['DOWN_SAMPLE_SCALE']
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

        if caller == "pipeline":
            self.createReferencesForPipeline(args, dataInfo)
        elif caller == "backend_management":
            self.createReferencesForBackend(args)

    def createReferencesForBackend(self, args = None):
        self.mountRenderPythonApps                    = u.toBool(self.general['MOUNT_RENDER_PYTHON_APPS'])
        self.mountRenderModules                       = u.toBool(self.general['MOUNT_RENDER_MODULES'])

    def createReferencesForPipeline(self, args = None, dataInfo = None):
        self.dataRootFolder                           = self.DATA_INPUT['DATA_ROOT_FOLDER']
        self.projectDataFolder                        = self.DATA_INPUT['PROJECT_DATA_FOLDER']

        #Process parameters
        self.projectName                              = os.path.basename(self.projectDataFolder)
        self.DATA_INPUT['PROJECT_NAME']               = self.projectName
        self.dataOutputFolder                         = os.path.join(self.dataOutputFolder, self.projectName)
        self.absoluteDataOutputFolder                 = os.path.join(self.projectDataFolder, self.dataOutputFolder)

        self.ribbons                                  = "" #ast.literal_eval(self.DATA_INPUT['RIBBONS'])
        self.sessions                                 = "" #ast.literal_eval(self.DATA_INPUT['SESSIONS'])

        #Over write any default values with any argument/values from the command line
        if args.firstsection != None:
            self.firstSection                         = args.firstsection
        else:
            self.firstSection                         = int(0)

        if args.lastsection != None:
            self.lastSection                         = args.lastsection
        else:
            self.lastSection                         = int(dataInfo['NumberOfSections']) - 1

        if args.ribbons  != None:
            self.ribbons                             = args.ribbons
        else:
            self.ribbons                             = list(dataInfo['RibbonFolders'].split(','))

        if args.sessions  != None:
            self.sessions                            = list(args.sessions.split(','))
        else:
            self.sessions                            = list(dataInfo['SessionFolders'].split(','))

        self.pipeline                                = args.pipeline
        self.overwritedata                           = args.overwritedata

        #Populate ini file sections so values passed on the command line are written
        #to the ini file in the data output folder
        self.DATA_INPUT['first_section']             = str(self.firstSection)
        self.DATA_INPUT['last_section']              = str(self.lastSection)
        self.DATA_INPUT['ribbons']                   = str(self.ribbons)
        self.DATA_INPUT['sessions']                  = str(self.sessions)
        self.DATA_INPUT['pipeline']                  = self.pipeline
        self.DATA_INPUT['overwritedata']             = str(self.overwritedata)

        #not that pretty...
        if args.renderprojectowner:
            self.renderProjectOwner = args.renderprojectowner
            self.DATA_INPUT['render_project_owner']  =  args.renderprojectowner


        #When used for input data
        #Create a "renderProject" to make things easier
        self.renderProject = rp.RenderProject(self.renderProjectOwner, self.projectName, self.renderHost, self.renderHostPort, self.clientScripts, self.memGB, self.logLevel)


    def getStateTableFileName(self, ribbon, session, sectnum):
        return os.path.join(self.absoluteDataOutputFolder, "statetables", "statetable_ribbon_%d_session_%d_section_%d"%(ribbon, session, sectnum))

    def write(self, fName):
        with open(fName, 'w') as configfile:
            self.config.write(configfile)

    def setupDockerMountName(self, localPath):
        #find the index of localPath in dataRootFolders variable
        mountIndex = 1
        for mount in self.mounts:
            if mount == localPath:
                self.dockerMountName = "/data_mount_" + str(mountIndex)
                break
            mountIndex = mountIndex + 1

        if len(self.dockerMountName) == 0:
            raise Exception("The data path: " + localPath + " is not valid")

    def toMount(self, aPath):
        if os.name == 'posix':
            return aPath #If on linux, the moounts looks the same inside and outside the container!
        #Find out index of path in DATA_ROOTS
        index = 0
        theMount = self.mounts[index][0]

        #Remove root part from aPath
        if aPath.startswith(theMount):
            aPath = aPath[len(theMount):]
        else:
            raise ValueError("The Path: " + aPath + " is not valid using the mount: " + theMOunt)

        aPath = posixpath.normpath(aPath.replace('\\', '/'))

        #prepare for join
        if aPath[0] == '/':
            aPath = aPath[1:]

        return posixpath.join(self.mounts[index][1], aPath)
