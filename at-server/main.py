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

stack_model = api.model('Stack', {
   'input' : fields.Nested(api.model('StackInput', {
      'owner' : fields.String,
      'project' : fields.String,
      'stack' : fields.String,
      'bounds' : fields.String(optional=True), 
   }))
})

@api.route('/owner/<string:owner>/project/<string:project>/stack/<string:stack>')
class Stack(Resource):
   @api.doc(responses={501: 'Not Implemented'})
   def get(self, owner, project, stack):
      stack = RenderStack(owner=owner, project_name=project, stack_name=stack)
      # Do something. Maybe report bounding box?
      api.abort(501)

   @api.expect(stack_model, validate=True)
   @api.doc(responses={200: 'Stack created'})
   def post(self, owner, project, stack):
      # Create a new stack
      #api.abort(404)
      input_stack = RenderStack(owner=api.payload['input']['owner'],
         project_name=api.payload['input']['project'],
         stack_name=api.payload['input']['stack'])
      output_stack = RenderStack(owner=owner, project_name=project, stack_name=stack)
      #    output_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])
      #    subv.create(input_stack, output_stack, bounds)
      return(api.payload['input'])

   @api.doc(responses={204: 'Delete successful', 404: 'No such subvolume to delete'})
   def delete(self, owner, project, stack):
      api.abort(404)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=50000, debug=True)
