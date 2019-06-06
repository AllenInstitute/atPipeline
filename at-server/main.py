#!/usr/bin/env python3

from flask import Flask, Blueprint, redirect, url_for
from flask_restplus import Resource, Api
from werkzeug.routing import Rule
#from sub_volume import SubVolume
#from render import RenderStack

from atpipeline import at_pipeline_api as atAPI

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
blueprint = Blueprint('atpipeline', __name__, url_prefix='/atpipeline')

default_api =    Api(blueprint, version=0.1, title='AT Pipeline API', doc='/swagger/')
backend_api     = default_api.namespace('backend',  description='Manage ATPipeline backend API.')
core_api        = default_api.namespace('core',     description='Core ATPipeline backend API.')
app.register_blueprint(blueprint)

#global
atp = atAPI.ATPipelineAPI()


##-------------------------------------------------------------------------------------------------------
app.url_map.add(Rule('/', endpoint='index'))
@app.endpoint('index')
def my_index():
    return "do something good"

app.url_map.add(Rule('/atpipeline', endpoint='index2'))
@app.endpoint('index2')
def my_index2():
    return "do something good2"

## 'core' ATPipeline API calls below --------------------------------------------------------------------

##@default_api.route('',  methods=['GET'])
##class Default(Resource):
##    def get(self):
##        return {'':''}

@default_api.route('/version')
class Version(Resource):

    def get(self):
        """Return the version of the ATPipeline API and related components
        """

        atp = atAPI.ATPipelineAPI()
        return {
                    'ATPipeline Version'            : atp.version,
                    'Web API Version'               : default_api.version,
                    'ATCore Python API version'     : atp.atcore.version,
                    'ATCore Docker Container Version':'0.5.3'
                }


@backend_api.route('/',  methods=['GET'])
class ATpipeline(Resource):
    def __init__(self, api=None, *args, **kwargs):
        self.backend    = atp.backend
        self.core       = atp.core

    def get(self):
        return {'':''}

@backend_api.route('/status',  methods=['GET'])
class Dummy(ATpipeline):
    def get(self):
        """Get backend running status"""
        return {'status':self.backend.get_status()}

@backend_api.route('/restart',  methods=['PUT'])
class Dummy(ATpipeline):
    def put(self):
        """Restart the ATPipeline backend"""
        return {'status':self.backend.restart()}

@backend_api.route('/stop',  methods=['PUT'])
class Dummy(ATpipeline):
    def put(self):
        """Stop the ATPipeline backend"""
        ret_value = self.backend.stop()
        return {'status':ret_value}

@backend_api.route('/start',  methods=['PUT'])
class Dummy(ATpipeline):
    def put(self):
        """Start the ATPipeline backend"""
        ret_value = self.backend.start()
        return {'status':ret_value}

@backend_api.route('/hostmounts',  methods=['GET'])
class Dummy(ATpipeline):
    def get(self):
        """Get host data mounts, that is, folders where AT Data may be retrieved and processed"""
        ret_value = self.backend.get_host_mounts()
        return ret_value

#---------------------- CORE ----------------------------------------------------------------------

#-------------- DATA related

@core_api.route('/datasets/<mount>',  methods=['GET'])
class Dummy(ATpipeline):
    def get(self, mount):
        """Get datasets for a mount"""
        ret_value = self.core.get_data_sets(mount)
        return ret_value

@core_api.route('/pipelines',  methods=['GET'])
class Dummy(ATpipeline):
    def get(self):
        """Get valid processing pipelines"""
        ret_value = self.core.get_valid_pipelines()
        return ret_value

@core_api.route('/dataset/select/<datarootfolder>',  methods=['POST'])
@core_api.route('/dataset/selected/',  methods=['GET'])
class Dummy(ATpipeline):
    def get(self):
        """Get selected dataset"""
        ret_value = self.core.get_selected_data_folder()
        return ret_value

    def post(self, datarootfolder):
        """Select dataset"""
        ret_value = self.core.select_data_folder(datarootfolder)
        return ret_value

@core_api.route('/owner/<o>/projects',  methods=['GET'])
class Dummy(ATpipeline):

    def get(self, o):
        """Get renderprojects by owner"""
        ret_value = self.core.get_projects_by_owner(o)
        return ret_value



#@app.route('/subvolume/create/input_stack/<string:input_stack>/output_stack/<string:output_stack>/bounds/<string:bounds>')
#def createsubvolume(_input_stack, _output_stack, _bounds):
#    i = _input_stack.split(',')
#    input_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])
#
#    i = _output_stack.split(',')
#    output_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])
#
#    subv = SubVolume()
#    subv.create(input_stack, output_stack, bounds)
#    return  (input_stack + output_stack)
#

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=50000, debug=True)
