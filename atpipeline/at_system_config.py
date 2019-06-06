import configparser
import os
import ast
from . import at_utils as u
import posixpath
from . import at_render_project as rp
import re


#Class that carries system and other parameters for the AT pipeline.
#Two 'clients' are using this class, the atbackend and the atcore.
#When used by the atcore, data processing flags are being populated, while that's not needed by
#the backend client

class ATSystemConfig:

    def __init__(self, args, client = 'atbackend'):

        #For convenience..
        self.args = args

        #Setup input parameters
        if args.configfolder:
            pass
        elif 'AT_SYSTEM_CONFIG_FOLDER' in os.environ:
            args.configfolder = os.environ['AT_SYSTEM_CONFIG_FOLDER']
        elif os.name == 'posix':
            args.configfolder = '/usr/local/etc/'
        else:
            raise Exception("No default config folder folder defined for %s. Set environment variable 'AT_SYSTEM_CONFIG_FOLDER' to the folder where the file 'at-system-config.ini' exists." % os.name)

        args.system_config_file = os.path.join(args.configfolder, 'at-system-config.ini')

        if client == 'atcore':
            if os.path.exists(args.configfile):
                args.configfile = os.path.abspath(args.configfile)
            else:
                args.configfile = os.path.join(args.configfolder, args.configfile)

            if os.path.isfile(args.configfile) == False:
                raise Exception("The data processing config file: " + args.configfile + " don't exist..")

        #Create the parser
        self.config = configparser.ConfigParser()

        #Check that file exists, otherwise raise an error
        if os.path.isfile(args.system_config_file) == False:
            raise Exception("The system config file: " + args.system_config_file + " don't exist..")

        #Read config files
        if client == 'atcore':
            self.config.read([args.system_config_file, args.configfile])
        else:
            self.config.read([args.system_config_file])

        #Check for over rides
        for flag in args.define:
            # Overrides from the command line in the form <section>.<setting>=<value>
            result = re.fullmatch(r'(.*?)\.(.*?)=(.*)', flag)
            if result:
                if result.group(1) not in self.config:
                    self.config[result.group(1)] = {}
                self.config[result.group(1)][result.group(2)] = result.group(3)
            else:
                raise Exception("Unable to config override: %s" % flag)

        #Setup some convenint names
        self.GENERAL                                       = self.config['GENERAL']
        self.atcore_ctr_name                               = self.config['GENERAL']['DOCKER_CONTAINER_PREFIX'] + '_atcore'

        self.mounts                                        = ast.literal_eval(self.GENERAL['DATA_ROOTS'])
        self.createCommonReferences()

        if client == 'atbackend':
            self.createReferencesForBackend(args)


    #The arguments passed here are captured from the commandline and will over ride any option
    #present in the system config file
    def createReferences(self, args = None, client = None, data_info = None):

        if client == "atcore":
            self.dataInfo = data_info
            self.createReferencesForPipeline(args, data_info)
        elif client == "atbackend":
            self.createReferencesForBackend(args)
        else:
            raise ValueError("No client set in the createreferences function..")

    def createCommonReferences(self):
        self.dataOutputFolder                         = self.GENERAL['PROCESSED_DATA_FOLDER']
        self.renderHost                               = self.GENERAL['RENDER_HOST']
        self.renderHostPort                           = int(self.GENERAL['RENDER_HOST_PORT'])
        self.logLevel                                 = self.GENERAL['LOG_LEVEL']
        self.clientScripts                            = self.GENERAL['CLIENT_SCRIPTS']
        self.render_mem_GB                            = self.GENERAL['RENDER_MEM_GB']
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


    def createReferencesForBackend(self, args = None):
        if args.atcoreimagetag == None:
            args.atcoreimagetag                         = self.GENERAL['AT_CORE_DOCKER_IMAGE_TAG']

        self.mountRenderPythonApps                    = u.toBool(self.GENERAL['MOUNT_RENDER_PYTHON_APPS'])
        self.mountRenderModules                       = u.toBool(self.GENERAL['MOUNT_RENDER_MODULES'])

    def createReferencesForPipeline(self, args = None, dataInfo = None):

        #SPARK stuff
        #self.SPARK                                         = self.config['SPARK']
        self.CREATE_LOWRES_STACKS                          = self.config['CREATE_LOWRES_STACKS']
        self.LOWRES_TILE_PAIR_CLIENT                       = self.config['LOWRES_TILE_PAIR_CLIENT']
        self.LOWRES_POINTMATCHES                           = self.config['LOWRES_POINTMATCHES']
        self.CREATE_2D_POINTMATCHES                        = self.config['CREATE_2D_POINTMATCHES']
        self.CREATE_HR_TILEPAIRS                           = self.config['CREATE_HR_TILEPAIRS']
        self.CREATE_HR_POINTMATCHES                        = self.config['CREATE_HR_POINTMATCHES']
        self.DROP_STITCHING_MISTAKES                       = self.config['DROP_STITCHING_MISTAKES']

        self.DATA_INPUT                                    = self.config['DATA_INPUT']

        self.dataRootFolder                           = os.path.abspath(self.DATA_INPUT['DATA_ROOT_FOLDER'])

        self.projectDataFolder                        = os.path.abspath(self.DATA_INPUT['PROJECT_DATA_FOLDER'])

        #Process parameters
        if args.projectname != None:
            self.project_name                          = args.projectname
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
            self.lastSection                         = int(dataInfo['atdata']['TotalNumberOfSections']) - 1

        if args.ribbons  != None:
            self.ribbons                             = list(args.ribbons.split(','))
        else:
            self.ribbons                             = dataInfo['atdata']['RibbonFolders']

        self.ribbons.sort()

        if args.sessions  != None:
            self.sessions                            = list(args.sessions.split(','))
        else:
            self.sessions                            = dataInfo['atdata']['SessionFolders']

        self.sessions.sort()
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

    def getNrOfSectionsInRibbon(self, ribbon):
        #Get ribbon index

        for r in self.dataInfo['atdata']['Ribbons']:
            if r['FolderName'] == ribbon:
                return r['NumberOfSections']


        raise ValueError('No such ribbon: %s in this dataset.'%(ribbon))

    def convertGlobalSectionIndexesToCurrentRibbon(self, _ribbon):
        #The ribbons are consecutive, with various number of sections
        #The user will supply a start, end section to process. That range may span
        #multiple ribbons and are numbered 1-N ("global" indexes).
        #When a ribbon is being processed, a "local" section index is used, starting at 0 for each
        #ribbon
        sectionIndices = []
        sectionIndicesArray = []

        #First create a "ribbon indices" arrays, holding global and local indices
        for i in range(self.dataInfo['atdata']['TotalNumberOfSections']):
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
