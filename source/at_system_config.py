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
        general                                      = config['GENERAL']
        self.dataRoots                               = ast.literal_eval(general['DATA_ROOTS'])
        self.mountRenderPythonApps                   = u.toBool(general['MOUNT_RENDER_PYTHON_APPS'])
        self.mountRenderModules                      = u.toBool(general['MOUNT_RENDER_MODULES'])

        self.JSONTemplatesFolder                     = general['JSON_TEMPLATES_FOLDER']

        #JSON Templates
        self.median_template                          = os.path.join(self.JSONTemplatesFolder, "median.json")
        self.stitching_template                       = os.path.join(self.JSONTemplatesFolder, "stitching.json")
        self.flatfield_template                       = os.path.join(self.JSONTemplatesFolder, "flatfield.json")
        self.deconvolution_template                   = os.path.join(self.JSONTemplatesFolder, "deconvolution.json")
        self.alignment_template                       = os.path.join(self.JSONTemplatesFolder, "roughalign.json")
        self.fine_alignment_template                  = os.path.join(self.JSONTemplatesFolder, "fine_align.json")
        self.registrationTemplate                     = os.path.join(self.JSONTemplatesFolder, "registration.json")

        self.dockerMountName = ""

    def setupDockerMountName(self, localPath):
        #find the index of localPath in dataRoots variable
        mountIndex = 1
        for mount in self.dataRoots:
            if mount == localPath:
                self.dockerMountName = "/data_mount_" + str(mountIndex)
                break
            mountIndex = mountIndex + 1

        if len(self.dockerMountName) == 0:
            raise Exception("The data path: " + localPath + " is not valid")


