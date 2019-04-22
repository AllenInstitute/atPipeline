import traceback
import os
from render_classes.render_stack import RenderStack, RenderStackBounds
from render_classes.sub_volume import SubVolume
import at_logging
logger = at_logging.create_logger('atPipeline')
import renderapi
from at_system_config import ATSystemConfig

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
        data_root = "c:\data"
        if os.name == 'posix':
            configFolder = '/usr/local/etc/'
        elif os.name == 'nt':
            #Read from environment
            configFolder = os.environ['AT_SYSTEM_CONFIG_FOLDER']


        system_config = ATSystemConfig(os.path.join(configFolder, 'at-system-config.ini'))
        system_config.DATA_INPUT['DATA_ROOT_FOLDER'] = data_root

        #This is the input
        INPUT = "Testing,M33,S1_Stitched".split(',')
        BOUNDS_INPUT = [1436,1894,4045,4422,400,403]
        if len(INPUT) < 3:
            raise ValueError("Bad input for creation of RenderStack object.")

        input_rs    = RenderStack(owner=INPUT[0], project_name=INPUT[1], stack_name=INPUT[2])
        bounds      = RenderStackBounds(BOUNDS_INPUT)

        render_project_owner    = 'Testing'

        args = {
            'host': system_config.renderHost,
            'port': system_config.renderHostPort,
            'owner': render_project_owner,
            'project': INPUT[1],
            'client_scripts': system_config.clientScripts
        }

        rc = renderapi.render.connect(**args)
        print (rc.DEFAULT_HOST)   #Weird naming.. DEFAULT_HOST is the host given by the args..

        test = renderapi.render.get_owners(render = rc)

        renderapi.stack.
        #Create a SubVolume object, pass renderhost parameters and system parameters
        sv = SubVolume(rc, system_config)

        #Create the subvolume on render
        output_stack_name = sv.create(input_rs, bounds)

        #Check that the stack was created on the host. if not, this function throws an Exception
        sv_stack_info = renderapi.stack.get_full_stack_metadata(render = rc, owner=render_project_owner, project=INPUT[1], stack=output_stack_name)

        print (sv_stack_info)


    except ValueError as e:
        logger.error('ValueError: ' + str(e))
        print(traceback.format_exc())

    except Exception as e:
        logger.error('Exception: ' + str(e))
        print(traceback.format_exc())




if __name__ == '__main__':
    main()
