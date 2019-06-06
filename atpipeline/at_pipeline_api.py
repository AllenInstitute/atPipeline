#-------------------------------------------------------------------------------
# Name:        at_pipeline_api
# Purpose:     Main entry point to various ATPipeline API's
# Created:     05/06/2019
#-------------------------------------------------------------------------------

from atpipeline import at_backend_api as atbAPI
from atpipeline import at_atcore_api as atcAPI

class ATPipelineAPI():
    def __init__(self):
        self.version = '0.34'
        self.backend = atbAPI.ATBackendAPI()
        self.core = atcAPI.ATCoreAPI()
