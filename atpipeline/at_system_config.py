import configparser
import os
import ast
from . import at_utils as u
import posixpath
from . import at_render_project as rp
import re

class ATSystemConfig:
    def __init__(self, iniFile, cmdFlags=[]):
        self.config = configparser.ConfigParser()

        #Check that file exists, otherwise raise an error
        if os.path.isfile(iniFile) == False:
            raise Exception("The file: " + iniFile + " don't exist..")

        self.config.read(iniFile)

        for flag in cmdFlags:
            # Overrides from the command line in the form <section>.<setting>=<value>
            result = re.fullmatch(r'(.*?)\.(.*?)=(.*)', flag)
            if result:
                if result.group(1) not in self.config:
                    self.config[result.group(1)] = {}
                self.config[result.group(1)][result.group(2)] = result.group(3)
            else:
                raise Exception("Unable to config override: %s" % flag)

        self.GENERAL                                       = self.config['GENERAL']

        #SPARK stuff
        self.SPARK                                         = self.config['SPARK']
        self.CREATE_LOWRES_STACKS                          = self.config['CREATE_LOWRES_STACKS']
        self.LOWRES_TILE_PAIR_CLIENT                       = self.config['LOWRES_TILE_PAIR_CLIENT']
        self.LOWRES_POINTMATCHES                           = self.config['LOWRES_POINTMATCHES']
        self.CREATE_2D_POINTMATCHES                        = self.config['CREATE_2D_POINTMATCHES']
        self.CREATE_HR_TILEPAIRS                           = self.config['CREATE_HR_TILEPAIRS']
        self.CREATE_HR_POINTMATCHES                        = self.config['CREATE_HR_POINTMATCHES']
        self.DROP_STITCHING_MISTAKES                       = self.config['DROP_STITCHING_MISTAKES']

        self.DATA_INPUT                                    = self.config['DATA_INPUT']

        self.mounts                                        = ast.literal_eval(self.GENERAL['DATA_ROOTS'])
        self.createCommonReferences()

    def getNrOfSectionsInRibbon(self, ribbon):
        #Get ribbon index
        ribbonIndex = self.ribbons.index(ribbon)

        #get number in dataInfo structure for index
        secsInRibbons = self.dataInfo['SectionsInRibbons']
        return secsInRibbons[ribbonIndex]

    def convertGlobalSectionIndexesToCurrentRibbon(self, _ribbon):
        #The ribbons are consecutive, with various number of sections
        #The user will supply a start, end section to process. That range may span
        #multiple ribbons and are numbered 1-N ("global" indexes).
        #When a ribbon is being processed, a "local" section index is used, starting at 0 for each
        #ribbon
        sectionIndices = []
        sectionIndicesArray = []

        #First create a "ribbon indices" arrays, holding global and local indices
        for i in range(self.dataInfo['NumberOfSections']):
            sectionIndices = {'global' : i, 'local' : -1, 'ribbon' : ''} #Simple dict helping with book keeping
            sectionIndicesArray.append(sectionIndices)

        #Populate 'local' indices, i.e. section index per ribbon. These starts at 0
        globalIndex = 0
        for ribbon in self.ribbons:
            nrOfSectionsInRibbon = self.getNrOfSectionsInRibbon(ribbon)
            for i in range(nrOfSectionsInRibbon):
                indices = sectionIndicesArray[globalIndex]
                indices['local'] = i
                indices['ribbon'] = ribbon
                globalIndex = globalIndex + 1

        #Now loop over first to last, and capture 'indices' falling on current input ribbon
        #First section starts at '1' (not zero)
        wantedIndices = []
        for i in range(self.firstSection, self.lastSection + 1):
            indices = sectionIndicesArray[i]
            if indices['ribbon'] == _ribbon:
                wantedIndices.append(indices)

        length = len (wantedIndices)
        if length == 0:
            return -1, -1
        return wantedIndices[0]['local'], wantedIndices[length - 1]['local']

    #The arguments passed here are captured from the commandline and will over ride any option
    #present in the system config file
    def createReferences(self, args = None, caller = None, dataInfo = None):
        self.dataInfo                                 = dataInfo
        if caller == "pipeline":
            self.createReferencesForPipeline(args, dataInfo)
        elif caller == "backend_management":
            self.createReferencesForBackend(args)

    def createCommonReferences(self):
        self.atCoreContainer                          = self.GENERAL['AT_CORE_DOCKER_CONTAINER_NAME']
        self.dataOutputFolder                         = self.GENERAL['PROCESSED_DATA_FOLDER']
        self.renderHost                               = self.GENERAL['RENDER_HOST']
        self.renderHostPort                           = int(self.GENERAL['RENDER_HOST_PORT'])
        self.logLevel                                 = self.GENERAL['LOG_LEVEL']
        self.clientScripts                            = self.GENERAL['CLIENT_SCRIPTS']
        self.render_mem_GB                            = self.GENERAL['RENDER_MEM_GB']
        #self.atCoreThreads                            = int(self.GENERAL['AT_CORE_THREADS'])
        #self.downSampleScale                          = self.GENERAL['DOWN_SAMPLE_SCALE']

        self.renderProjectOwner                       = self.GENERAL['RENDER_PROJECT_OWNER']

        self.referenceChannelRegistration             = self.GENERAL['REFERENCE_CHANNEL_REGISTRATION']
        self.JSONTemplatesFolder                      = self.GENERAL['JSON_TEMPLATES_FOLDER']

        #JSON Templates
        self.median_template                          = os.path.join(self.JSONTemplatesFolder, "median.json")
        self.stitching_template                       = os.path.join(self.JSONTemplatesFolder, "stitching.json")
        self.flatfield_template                       = os.path.join(self.JSONTemplatesFolder, "flatfield.json")
        self.deconvolution_template                   = os.path.join(self.JSONTemplatesFolder, "deconvolution.json")
        self.alignment_template                       = os.path.join(self.JSONTemplatesFolder, "roughalign.json")
        self.fine_alignment_template                  = os.path.join(self.JSONTemplatesFolder, "fine_align.json")
        self.registration_template                    = os.path.join(self.JSONTemplatesFolder, "registration.json")

        #Deconvolution parameters
##        self.channels                                 = ast.literal_eval(self.deconv['CHANNELS'])
##        self.bgrdSize                                 = ast.literal_eval(self.deconv['BGRD_SIZE'])
##        self.scaleFactor                              = ast.literal_eval(self.deconv['SCALE_FACTOR'])
##        self.numIter                                  = int(self.deconv['NUM_ITER'])
##        self.ch405                                    = self.config['DECONV_405']
##        self.ch488                                    = self.config['DECONV_488']
##        self.ch594                                    = self.config['DECONV_594']
##        self.ch647                                    = self.config['DECONV_647']

##        #Alignment parameters
##        self.poolSize                                 = int(self.align['POOL_SIZE'])
##        self.edgeThreshold                            = int(self.align['EDGE_THRESHOLD'])
##        self.scale                                    = float(self.align['SCALE'])
##        self.distance                                 = int(self.align['DISTANCE'])
##        self.siftMin                                  = float(self.align['SIFTMIN'])
##        self.siftMax                                  = float(self.align['SIFTMAX'])
##        self.siftSteps                                = int(self.align['SIFTSTEPS'])
##        self.renderScale                              = float(self.align['RENDERSCALE'])



##        #Tilepair client
##        self.excludeCornerNeighbors                   = u.toBool(self.tp_client['EXCLUDE_CORNER_NEIGHBOURS'])
##        self.excludeSameSectionNeighbors              = u.toBool(self.tp_client['EXCLUDE_SAME_SECTION_NEIGHBOR'])
##        self.zNeighborDistance                        = int(self.tp_client['Z_NEIGHBOR_DISTANCE'])
##        self.xyNeighborFactor                         = float(self.tp_client['XY_NEIGHBOR_FACTOR'])

    def createReferencesForBackend(self, args = None):
        self.mountRenderPythonApps                    = u.toBool(self.GENERAL['MOUNT_RENDER_PYTHON_APPS'])
        self.mountRenderModules                       = u.toBool(self.GENERAL['MOUNT_RENDER_MODULES'])

    def createReferencesForPipeline(self, args = None, dataInfo = None):
        self.dataRootFolder                           = os.path.abspath(self.DATA_INPUT['DATA_ROOT_FOLDER'])

        self.projectDataFolder                        = os.path.abspath(self.DATA_INPUT['PROJECT_DATA_FOLDER'])

        #Process parameters
        if args.project_name != None:
            self.project_name                          = args.project_name
        else:
            self.project_name                          = os.path.basename(self.projectDataFolder)

        self.DATA_INPUT['PROJECT_NAME']               = self.project_name
        self.dataOutputFolder                         = os.path.join(self.dataOutputFolder, self.project_name)
        self.absoluteDataOutputFolder                 = os.path.join(self.projectDataFolder, self.dataOutputFolder)

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
        self.renderProject = rp.RenderProject(self.renderProjectOwner, self.project_name, self.renderHost, self.renderHostPort, self.clientScripts, self.render_mem_GB, self.logLevel)

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
        nrOfMounts = len(self.mounts);
        found = False
        for index in range(nrOfMounts):
            theMount = self.mounts[index][0]

            aPathLowerCase = aPath.lower()
            theMountLowerCase = theMount.lower()
            #Remove root part from aPath
            if aPathLowerCase.startswith(theMountLowerCase):
                aPath = aPath[len(theMount):]
                found = True
                break

        if not found:
            raise Exception('Failed finding mount for path: ' + aPath)

        aPath = posixpath.normpath(aPath.replace('\\', '/'))

        #prepare for join
        if aPath[0] == '/':
            aPath = aPath[1:]

        return posixpath.join(self.mounts[index][1], aPath)
