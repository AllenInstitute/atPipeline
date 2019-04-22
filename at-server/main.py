#!/usr/bin/env python3

from flask import Flask, Blueprint, redirect, url_for
from flask_restplus import Resource, Api

from sub_volume import SubVolume
from render import RenderStack

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
        return {'version': api.version}

@api.route('/status')
class Status(Resource):
    def get(self):
        return {}

@app.route('/subvolume/create/input_stack/<string:input_stack>/output_stack/<string:output_stack>/bounds/<string:bounds>')
def createsubvolume(_input_stack, _output_stack, _bounds):
    i = _input_stack.split(',')
    input_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])

    i = _output_stack.split(',')
    output_stack = RenderStack(owner = i[0], project_name = i[1], stack_name = i[2])

    subv = SubVolume()
    subv.create(input_stack, output_stack, bounds)
    return  (input_stack + output_stack)

@app.route('/guest/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest

@app.route('/admin')
def hello_admin():
   return 'Hello Admin'

@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
      return redirect(url_for('hello_admin'))
   else:
      return redirect(url_for('hello_guest',guest = name))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=50000, debug=True)
