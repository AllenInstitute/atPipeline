#-------------------------------------------------------------------------------
# Name:        at_backend_api
# Purpose:     Manage the ATPipeline backend
# Author:      matsk
# Created:     05/06/2019
#-------------------------------------------------------------------------------
import argparse
import os
import json
from atpipeline import at_logging, at_docker_manager, at_system_config
from atpipeline import at_backend_arguments
from atpipeline import at_utils as u

class ATBackendAPI():
    def __init__(self):
        self.version = '0.5'
        self.status = 'stopped'

        parser = argparse.ArgumentParser('atbackend')
        at_backend_arguments.add_arguments(parser)
        args = parser.parse_args()

        self.system_config = at_system_config.ATSystemConfig(args, client = 'atbackend')
        self.docker_manager = at_docker_manager.DockerManager(self.system_config)

    def get_status(self):
        return self.status

    def get_host_mounts(self):
        return self.docker_manager.mounts

    def start(self):
        self.status = 'running'
        return self.status

    def stop(self):
        self.status = 'stopped'
        return self.status

    def restart(self):
        self.stop()
        self.start()
        return self.status


