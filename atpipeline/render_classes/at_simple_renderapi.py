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
import subprocess
import logging
import renderapi
from atpipeline import at_logging, at_system_config

logger = logging.getLogger('atPipeline')

#Simple wrapper class for renderapi
class SimpleRenderAPI:

    def __init__(self, sys_config:at_system_config.ATSystemConfig, owner = None):

        self.sys_config = sys_config
        if owner == None:
            self.owner = sys_config.args.renderprojectowner
        else:
            self.owner      = owner

        self.render_args = {
                'host': sys_config.renderHost,
                'port': sys_config.renderHostPort,
                'owner': self.owner,
                'project': "",
                'client_scripts': sys_config.clientScripts
            }

        self.render_client = renderapi.render.connect(**self.render_args)

    def get_render_client(self):
        return self.render_client

    def get_stacks(self, owner, project):
        self.render_args['owner'] = owner
        self.render_args['project'] = project
        rc = renderapi.render.connect(**self.render_args)
        return renderapi.render.get_stacks_by_owner_project(render = rc)

    def get_render_stack_meta_data(self, owner, project, stack):
        self.render_args['owner'] = owner
        self.render_args['project'] = project
        self.render_args['stack'] = stack
        rc = renderapi.render.connect(**self.render_args)

        return False #renderapi.render(render = rc)

    def delete_stacks(self, owner, project):
        print ("Deleting stacks in project: " + project + " for owner " + owner)

        self.render_args['owner'] = owner
        self.render_args['project'] = project

        rc = renderapi.render.connect(**self.render_args)
        stacks = renderapi.render.get_stacks_by_owner_project(render = rc)

        print('Deleting stacks:', stacks)
        stackcount = 0
        for stack in stacks:
            print('Deleting stack ' + stack)
            renderapi.stack.delete_stack(stack, render=rc)
            stackcount = stackcount + 1

        return stackcount

    def get_projects(self, owner):
        self.render_args['owner'] = owner
        rc = renderapi.render.connect(**self.render_args)

        return renderapi.render.get_projects_by_owner(render = rc)

    def delete_project(self, owner, project):
        self.render_args['owner'] = owner
        self.render_args['project'] = project
        rc = renderapi.render.connect(**self.render_args)

        #Find a way todo this
        return False #renderapi.render.get_projects_by_owner(render = rc)

    def get_matchcollections(self, owner):
        self.render_args['owner'] = owner
        rc = renderapi.render.connect(**self.render_args)
        collections = renderapi.pointmatch.get_matchcollections(owner, render = rc)
        return collections

    def get_matchcollection(self, owner, match_collection):
        self.render_args['owner'] = owner
        rc = renderapi.render.connect(**self.render_args)
        collections = renderapi.pointmatch.get_matchcollections(owner, render = rc)

        for c in collections:
            if c['collectionId']['name'] == match_collection:
                return c
        logger.warning('No such match collection: "' + match_collection + '"')
        return None

    def delete_match_context(self, owner, match_collection):

        print ("Deleting match context '" + match_collection + "' for owner " + owner)
        collections = self.get_matchcollections(owner)

        exists = False
        for c in collections:
            if c['collectionId']['name'] == match_collection:
                exists = True

        if exists == True:
            self.render_args['owner'] = owner
            rc = renderapi.render.connect(**self.render_args)
            return renderapi.pointmatch.delete_collection(match_collection, render = rc)

        logger.warning('No such match collection: "' + matchCollection + '"')
        return None


    def clone_stack(self, input_stack, output_stack, render_project):

        return renderapi.stack.clone_stack(input_stack, output_stack, owner=render_project.owner, project=render_project.project_name,  render=self.get_render_client())