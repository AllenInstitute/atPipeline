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
from atpipeline.render_classes import sub_volume
from atpipeline.render_classes import render_stack
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

    def get_version(self):
        return self.version

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
        projects = self.simple_renderapi.get_projects(o)
        return projects

    def delete_project_by_owner(self, o, p):
        v = self.simple_renderapi.delete_project(o, p)
        return v
    #----------- Stacks
    def get_stack_by_owner_project(self, o, p, s):
        projects = self.simple_renderapi.get_stacks(o, p, s)
        return projects

    def get_stacks_by_owner_project(self, o, p):
        projects = self.simple_renderapi.get_stacks(o, p)
        return projects

    def delete_stacks_by_owner_project(self, o, p):
        count = self.simple_renderapi.delete_stacks(o, p)
        return count

    def create_subvolume_stack(self, input_stack:render_stack.RenderStack, bounds:render_stack.RenderStackBounds, output_stack:render_stack.RenderStack = None):
        sv = sub_volume.SubVolume(self.system_config, self.simple_renderapi)
        sv.create(input_stack, bounds, output_stack)


    #---------- Server Data
    def select_data_folder(self, datafolder):
        self.selected_data_folder = datafolder
        return os.path.exists(self.selected_data_folder)

    def get_selected_data_folder(self):
        return self.selected_data_folder
