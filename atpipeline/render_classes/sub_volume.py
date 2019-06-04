import os
import timeit
import subprocess
import at_logging
from at_system_config import ATSystemConfig
from render_classes.render_stack import RenderStack, RenderStackBounds
from renderapi.render import RenderClient

from flask_restplus import Resource, Api
logger = at_logging.create_logger('atPipeline')

class SubVolume(Resource):

    def __init__(self, rc:RenderClient, sc:ATSystemConfig):

        self.render_client = rc
        self.system_config = sc

        #print (self.render_client.

    def get(self):
        pass

    def post(self):
        pass

    def create(self, input_stack:RenderStack, bounds:RenderStackBounds, output_stack:RenderStack = None):

        pool_size    = self.system_config.poolSize

        if output_stack == None:
            #Create an outputstack
            ostack = RenderStack.copyfrom(input_stack)
        else:
            ostack = RenderStack.copyfrom(output_stack)

        ostack.stack_name = ostack.stack_name + "_SubVolume"

        #Create output data folder
        output_data_folder = os.path.join(self.system_config.DATA_INPUT['DATA_ROOT_FOLDER'], ostack.project_name, "processed", ostack.project_name, "subvolumes", ostack.stack_name)
        #upload acquisition stacks
        cmd = "docker exec " + sc.atcore_ctr_name + " python -m renderapps.stack.create_subvolume_stack"
        cmd = cmd + " --render.memGB 5G"
        cmd = cmd + " --log_level INFO"

        cmd = cmd + " --render.host %s"             %(self.render_client.DEFAULT_HOST)
        cmd = cmd + " --render.client_scripts %s"   %(self.render_client.DEFAULT_CLIENT_SCRIPTS)
        cmd = cmd + " --render.port %s"             %(self.render_client.DEFAULT_PORT)
        cmd = cmd + " --render.owner %s"            %(input_stack.owner)
        cmd = cmd + " --render.project %s"          %(input_stack.project_name)
        cmd = cmd + " --input_stack %s"             %(input_stack.stack_name)
        cmd = cmd + " --directory %s "              %(self.system_config.toMount(output_data_folder))
        cmd = cmd + " --output_stack %s"            %(ostack.stack_name)
        cmd = cmd + " --minX %d"                    %(bounds.minX)
        cmd = cmd + " --maxX %d"                    %(bounds.maxX)
        cmd = cmd + " --minY %d"                    %(bounds.minY)
        cmd = cmd + " --maxY %d"                    %(bounds.maxY)
        cmd = cmd + " --minZ %d"                    %(bounds.minZ)
        cmd = cmd + " --maxZ %d"                    %(bounds.maxZ)
        cmd = cmd + " --pool_size %d"               %(pool_size)

        #Run =============
        logger.info("Running: " + cmd.replace('--', '\n--'))

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        for line in proc.stdout.readlines():
            logger.info(line.rstrip())

        return ostack.stack_name