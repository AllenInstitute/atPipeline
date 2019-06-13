#!/usr/bin/env python3
from flask import Flask, Blueprint, redirect, url_for
from flask_restplus import Resource, Api
from werkzeug.routing import Rule
from atpipeline import at_pipeline_api as atAPI
from atpipeline.render_classes import sub_volume
from atpipeline.render_classes import render_stack

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
blueprint = Blueprint('atpipeline', __name__, url_prefix='/api')

api                 = Api(blueprint, version=0.1, default='Miscellaneous', default_label='Miscellaneous functions', title='AT Pipeline API', doc='/swagger/')
backend_api         = api.namespace('backend',              title= 'Test', default='Backend', default_label='Server Backend API\'s', description='ATPipeline Backend API\'s')
server_data_api     = api.namespace('serverdata',           description='Server Data API\'s')
stacks_data_api     = api.namespace('stacks',               description='Stacks Data API\'s')
render_projects_api = api.namespace('projects',             description='Render Projects API\'s')
stitching_api       = api.namespace('stitching',            description='Stithcing API\'s')
rough_align_api     = api.namespace('roughalign',           description='Rough Aligns API\'s')
fine_align_api      = api.namespace('finealign',            description='Fine Align API\'s')
register_api        = api.namespace('registers',            description='Register API\'s')
app.register_blueprint(blueprint)

#global ATPipeline API object
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

## 'server_data_api' ATPipeline API calls below --------------------------------------------------------------------

##@api.route('',  methods=['GET'])
##class Default(Resource):
##    def get(self):
##        return {'':''}

@api.route('/version')
class Version(Resource):

    def get(self):
        """Return the version of the ATPipeline API and related components
        """
        atp = atAPI.ATPipelineAPI()
        return {
                    'ATPipeline Version'            : atp.version,
                    'Web API Version'               : api.version,
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
class Status(ATpipeline):
    def get(self):
        """Get backend running status"""
        return {'status':self.backend.get_status()}

@backend_api.route('/restart',  methods=['PUT'])
class Restart(ATpipeline):
    def put(self):
        """Restart the ATPipeline backend"""
        return {'status':self.backend.restart()}

@backend_api.route('/stop',  methods=['PUT'])
class Stop(ATpipeline):
    def put(self):
        """Stop the ATPipeline backend"""
        ret_value = self.backend.stop()
        return {'status':ret_value}

@backend_api.route('/start',  methods=['PUT'])
class Start(ATpipeline):
    def put(self):
        """Start the ATPipeline backend"""
        ret_value = self.backend.start()
        return {'status':ret_value}

@backend_api.route('/hostmounts',  methods=['GET'])
class HostMounts(ATpipeline):
    def get(self):
        """Get host data mounts, that is, folders where AT Data may be retrieved and processed"""
        ret_value = self.backend.get_host_mounts()
        return ret_value

#---------------------- CORE ----------------------------------------------------------------------
#-------------- Server data related
@server_data_api.route('/datasets/<mount>',  methods=['GET'])
class ServerDataset(ATpipeline):
    def get(self, mount):
        """Get datasets for a mount"""
        ret_value = self.core.get_data_sets(mount)
        return ret_value

@server_data_api.route('/pipelines',  methods=['GET'])
class Pipelines(ATpipeline):
    def get(self):
        """Get valid processing pipelines"""
        ret_value = self.core.get_valid_pipelines()
        return ret_value

@server_data_api.route('/dataset/select/<datarootfolder>',  methods=['POST'])
@server_data_api.route('/dataset/selected/',  methods=['GET'])
class Dataset(ATpipeline):
    def get(self):
        """Get selected dataset"""
        ret_value = self.core.get_selected_data_folder()
        return ret_value

    def post(self, datarootfolder):
        """Select dataset on the server. The selected dataset can be processed by data processing endpoints"""
        ret_value = self.core.select_data_folder(datarootfolder)
        return ret_value

#---- Stacks data API's
@stacks_data_api.route('/owner/<o>/project/<p>',  methods=['GET','DELETE'])
class Stacks(ATpipeline):

    def get(self, o, p):
        """Get stacks by owner and project"""
        ret_value = self.core.get_stacks_by_owner_project(o, p)
        return ret_value

    def delete(self, o, p):
        """Delete stacks (all!) by owner and project"""
        ret_value = self.core.delete_stacks_by_owner_project(o, p)
        return ret_value

@stacks_data_api.route('/owner/<o>/project/<p>/stack<s>',  methods=['GET'])
class Stack(ATpipeline):
    def get(self, o, p, s):
        """Get stack metadata for specified stack"""
        ret_value = self.core.get_stack_by_owner_project(o, p, s)
        return ret_value

#Creation of a substack takes an input stack and an optional bounds parameter
#If no parameter are supplied, the new stack is an exact clone of the source stack
@stacks_data_api.route('/owner/<owner>/project/<project>/source_stack/<source_stack>/bounds/<string:bounds>',  methods=['PUT'])
class CreateSubVolume(ATpipeline):
    def put(self, owner, project, source_stack, bounds):
        """Create a substack, cutout from an existsting stackk"""

        input_stack = render_stack.RenderStack(owner = owner, project=project, stack_name = source_stack)
        bounds = render_stack.RenderStackBounds(bounds)

        ret_value = self.core.create_subvolume_stack(input_stack, bounds)
        return ret_value

#---- Projects API's
@render_projects_api.route('/owner/<o>/projects',  methods=['GET'])
@render_projects_api.route('/owner/<o>/project/<p>',  methods=['DELETE'])
class Projects(ATpipeline):

    def get(self, o):
        """Get renderprojects by owner"""
        ret_value = self.core.get_projects_by_owner(o)
        return ret_value

    def delete(self, o, p):
        """Delete render project with all its stacks and match collections"""
        ret_value = self.core.delete_project_by_owner(o,p)
        return ret_value

#---- Stitching API's
#---- Rough Align API's
#---- Fine Align API's
#---- Registration API's

#@app.route('/subvolume/create/input_stack/<string:input_stack>/output_stack/<string:output_stack>/bounds/<string:bounds>')
#def createsubvolume(_input_stack, _output_stack, _bounds):
#
#    i = _output_stack.split(',')

#
#    subv = SubVolume()
#    subv.create(input_stack, output_stack, bounds)
#    return  (input_stack + output_stack)
#

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=50000, debug=True)
