import configparser
import os
import ast
import atutils as u

class ATSystemConfig:
    def __init__(self, iniFile):
        config = configparser.ConfigParser()

        #Check that file exists, otherwise raise an error
        if os.path.isfile(iniFile) == False:
            raise Exception("The file: " + iniFile + " don't exist..")

        config.read(iniFile)
        general                                       = config['GENERAL']
        deconv                                        = config['DECONV']
        align                                         = config['ALIGN']
        tp_client                                     = config['TILE_PAIR_CLIENT']
        SPARK_SEC                                     = config['SPARK']

        self.dataRoots                                = ast.literal_eval(general['DATA_ROOTS'])
        self.mountRenderPythonApps                    = u.toBool(general['MOUNT_RENDER_PYTHON_APPS'])
        self.mountRenderModules                       = u.toBool(general['MOUNT_RENDER_MODULES'])
        self.atCoreContainer                          = general['AT_CORE_DOCKER_CONTAINER']
        self.atCoreThreads                            = int(general['AT_CORE_THREADS'])
        self.downSampleScale                          = general['DOWN_SAMPLE_SCALE']

        self.renderHost                               = general['RENDER_HOST']
        self.renderHostPort                           = int(general['RENDER_HOST_PORT'])
        self.logLevel                                 = general['LOG_LEVEL']
        self.clientScripts                            = general['CLIENT_SCRIPTS']
        self.memGB                                    = general['MEM_GB']

        self.JSONTemplatesFolder                      = general['JSON_TEMPLATES_FOLDER']

        #JSON Templates
        self.median_template                          = os.path.join(self.JSONTemplatesFolder, "median.json")
        self.stitching_template                       = os.path.join(self.JSONTemplatesFolder, "stitching.json")
        self.flatfield_template                       = os.path.join(self.JSONTemplatesFolder, "flatfield.json")
        self.deconvolution_template                   = os.path.join(self.JSONTemplatesFolder, "deconvolution.json")
        self.alignment_template                       = os.path.join(self.JSONTemplatesFolder, "roughalign.json")
        self.fine_alignment_template                  = os.path.join(self.JSONTemplatesFolder, "fine_align.json")
        self.registrationTemplate                     = os.path.join(self.JSONTemplatesFolder, "registration.json")

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

        #SPARK stuff
        self.SPARK = {}
        self.SPARK['driverMemory']                    = SPARK_SEC['DRIVER_MEMORY']
        self.SPARK['executorMemory']                  = SPARK_SEC['EXECUTOR_MEMORY']
        self.SPARK['executorCores']                   = SPARK_SEC['EXECUTOR_CORES']
        self.SPARK['maxFeatureCacheGb']               = SPARK_SEC['MAX_FEATURE_CACHE_GB']

        self.ch405                                    = config['DECONV_405']
        self.ch488                                    = config['DECONV_488']
        self.ch594                                    = config['DECONV_594']
        self.ch647                                    = config['DECONV_647']

        #Tilepair client
        self.excludeCornerNeighbors                   = u.toBool(tp_client['EXCLUDE_CORNER_NEIGHBOURS'])
        self.excludeSameSectionNeighbors              = u.toBool(tp_client['EXCLUDE_SAME_SECTION_NEIGHBOR'])
        self.zNeighborDistance                        = int(tp_client['Z_NEIGHBOR_DISTANCE'])
        self.xyNeighborFactor                         = float(tp_client['XY_NEIGHBOR_FACTOR'])


        self.dockerMountName = ""

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


