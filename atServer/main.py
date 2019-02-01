#!/usr/bin/env python3

from flask import Flask, Blueprint, redirect, url_for
from flask_restplus import Resource, Api

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)
