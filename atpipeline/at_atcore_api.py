#-------------------------------------------------------------------------------
# Name:        at_atcoreAPI
# Purpose:     API exposing the core of the ATPipeline
# Created:     05/06/2019
#-------------------------------------------------------------------------------
import argparse
import os
import json
#import renderapi
from atpipeline.render_classes import at_simple_renderapi as rapi
from atpipeline import at_system_config
from atpipeline import at_atcore_arguments
from atpipeline import at_utils as u

class ATCoreAPI():
    def __init__(self):

        self.version = '0.5'

        parser = argparse.ArgumentParser()
        at_atcore_arguments.add_arguments(parser)
        args = parser.parse_args()

        self.system_config = at_system_config.ATSystemConfig(args, client = 'atcore')
        self.simple_renderapi = rapi.SimpleRenderAPI(self.system_config)
        self.selected_data_folder = None

        self.pipelines = ['stitch', 'roughalign', 'finealign', 'register', 'singletile']

    def get_valid_pipelines(self):
        return self.pipelines

    def get_data_sets(self, mount):
        #Get folders in supplied mount
        return os.listdir(mount)

    def get_data_info(self, dataroot):
        cmd = 'docker exec ' + self.system_config.atcore_ctr_name + ' atcli --datasummary --data ' + self.system_config.toMount(dataroot)
        dataInfo = json.loads(u.getJSON(cmd))
        return dataInfo

    #----------- Projects
    def get_projects_by_owner(self, o):
        projects = self.simple_renderapi.get_projects_by_owner(o)
        return projects

    #----------- Stacks
    def get_stacks_by_owner_project(self, o, p):
        projects = self.simple_renderapi.get_stacks_by_owner_project(o, p)
        return projects

    def delete_stacks_by_owner_project(self, o, p):
        count = self.simple_renderapi.delete_stacks(o, p)
        return count
    #---------- Server Data
    def select_data_folder(self, datafolder):
        self.selected_data_folder = datafolder
        return os.path.exists(self.selected_data_folder)

    def get_selected_data_folder(self):
        return self.selected_data_folder
