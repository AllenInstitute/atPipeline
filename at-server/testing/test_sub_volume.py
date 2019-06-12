import traceback
import os
import argparse

from atpipeline import at_logging
logger = at_logging.create_logger('atPipeline')

from atpipeline.render_classes.render_stack import RenderStack, RenderStackBounds
from atpipeline.render_classes import at_simple_renderapi
from atpipeline.render_classes.sub_volume import SubVolume
from atpipeline import at_system_config
from atpipeline import at_atcore_arguments

#The ATServer createSubvolume API will require
# input stack name
# owner
# project name
# outputstack name
# output owner
# output project name
# volume bounds
# output data folder (this seem to just create an empty folder at the moment)
#
# The function will check that the input stack and input bounds are valid. If not valid, the function will fail with
# appropriate error message.
# Observe that the outputstacks owner don't need to be the same as the original stack. For example the input stack may be
# (ATServer, M33, stichted) and the subvolume stack may be (SubVolumes, M33, SubVolume1)
#
# Other Requirements
# The function will load the systems config file, and fetch render host, and processing info from there.

def main():
    try:
        parser = argparse.ArgumentParser()
        at_atcore_arguments.add_arguments(parser)
        args = parser.parse_args()
        system_config = at_system_config.ATSystemConfig(args, client = 'atcore')

        #This is the input
        render_project_owner     = 'PyTest'
        project_name            = 'pytest_Q1023'
        source_stack            = 'S2_Session2'

        bounds = [1436,1894,4045,4422,1000,1005]

        input_stack = RenderStack(owner=render_project_owner, project_name=project_name, stack_name=source_stack)
        bounds      = RenderStackBounds(bounds)

        args = {
            'host': system_config.renderHost,
            'port': system_config.renderHostPort,
            'owner': render_project_owner,
            'project': project_name,
            'client_scripts': system_config.clientScripts
        }

        simple_render = at_simple_renderapi.SimpleRenderAPI(system_config)

        #Create a SubVolume object, pass renderhost parameters and system parameters
        sv = SubVolume(system_config, simple_render)

        #Create the subvolume on render
        output_stack_name = sv.create(input_stack, bounds)

        #Check that the stack was created on the host. if not, this function throws an Exception
        #sv_stack_info = renderapi.stack.get_full_stack_metadata(render = rc, owner = render_project_owner, project=INPUT[1], stack=output_stack_name)

        print (sv_stack_info)


    except ValueError as e:
        logger.error('ValueError: ' + str(e))
        print(traceback.format_exc())

    except Exception as e:
        logger.error('Exception: ' + str(e))
        print(traceback.format_exc())




if __name__ == '__main__':
    main()
