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
class RenderAPI:

    def __init__(self, sys_config : at_system_config.ATSystemConfig, owner = None):
        self.sys_config = sys_config
        self.owner      = owner

        self.render_args = {
                'host': sys_config.renderHost,
                'port': sys_config.renderHostPort,
                'owner': owner,
                'project': "",
                'client_scripts': sys_config.clientScripts
            }

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


    def delete_match_context(self, owner, matchCollection):
        self.render_args['owner'] = owner
        print ("Deleting match context '" + matchCollection + "' for owner " + owner)
        rc = renderapi.render.connect(**self.render_args)

        collections = renderapi.pointmatch.get_matchcollections(owner, render = rc)

        exists = False
        for c in collections:
            if c['collectionId']['name'] == matchCollection:
                exists = True

        if exists == True:
            return renderapi.pointmatch.delete_collection(matchCollection, render = rc)

        logger.warning('No such match collection: "' + matchCollection + '"')
        return None
