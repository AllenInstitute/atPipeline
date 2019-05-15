#!/usr/bin/env python3

from flask import Flask, Blueprint, redirect, url_for
from flask_restplus import Resource, Api, fields

import atpipeline
from atpipeline.render_classes.sub_volume import SubVolume
from atpipeline.render_classes.render_stack import RenderStack

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version=0.1, title='AT Pipeline API', doc='/swagger/')
app.register_blueprint(blueprint)

@app.route('/')
def index():
   return redirect(url_for('api.doc'))

@api.route('/version')
class Version(Resource):
   def get(self):
      return {
         'api': api.version,
         'atpipeline': atpipeline.__version__
      }

@api.route('/status')
class Status(Resource):
   # TODO: What should we report?
   def get(self):
      return {'status': 'UNKNOWN'}

subvolume_fields = api.model('Resource', {
   'input_stack' : fields.String,
   'bounds' : fields.String(default=None)
})

@api.route('/subvolume/<string:stack_name>')
class Subvolume(Resource):
   @api.doc(responses={501: 'Not Implemented'})
   def get(self, stack_name):
      api.abort(501)

   @api.expect(subvolume_fields)
   @api.doc(responses={200: 'Stack created'})
   def post(self, stack_name):
      # Create a new stack
      api.abort(404)

   @api.doc(responses={204: 'Delete successful', 404: 'No such subvolume to delete'})
   def delete(self, stack_name):
      api.abort(404)

@app.route('/subvolume/create/input_stack/<string:input_stack>/output_stack/<string:output_stack>/bounds/<string:bounds>')
def createsubvolume(_input_stack, _output_stack, _bounds):
   # TODO: Why can't we call renderapps.stack.create_subvolume_stack directly?
   i = _input_stack.split(',')
   input_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])

   i = _output_stack.split(',')
   output_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])

   subv = SubVolume()
   subv.create(input_stack, output_stack, bounds)
   return  (input_stack + output_stack)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=50000, debug=True)
