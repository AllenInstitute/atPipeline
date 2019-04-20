import traceback
import os
from render_classes.render_stack import RenderStack, RenderStackBounds
from render_classes.sub_volume import SubVolume
import at_logging
logger = at_logging.create_logger('atPipeline')
import renderapi
from at_system_config import ATSystemConfig

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

        inp = "Testing,M33,S1_Stitched".split(',')
        if len(inp) < 3:
            raise ValueError("Bad input for creation of RenderStack object.")

        input_rs    = RenderStack(owner=inp[0], project_name=inp[1], stack_name=inp[2])
        bounds      = RenderStackBounds([0,1,2,3,4,5])

        args = {
        'host': 'localhost',
        'port': 80,
        'owner': 'Testing',
        'project': 'M33',
        'client_scripts': '/shared/render/render-ws-java-client/src/main/scripts'
        }

        rc = renderapi.render.connect(**args)


        print (rc.DEFAULT_HOST)   #Weird naming.. DEFAULT_HOST is the host given by the args..

        test = renderapi.render.get_owners(render = rc)
        sv = SubVolume(rc, system_config)
        sv.create(input_rs, bounds)


    except ValueError as e:
        logger.error('ValueError: ' + str(e))
        print(traceback.format_exc())

    except Exception as e:
        logger.error('Exception: ' + str(e))
        print(traceback.format_exc())




if __name__ == '__main__':
    main()
