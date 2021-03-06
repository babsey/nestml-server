#!/usr/bin/env python3

import os
import sys
import shutil

from flask import abort, Flask, jsonify, request
from flask_cors import CORS, cross_origin

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response
import traceback

import nest
import pynestml
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

HOST = os.environ.get('NESTML_SERVER_HOST', '127.0.0.1')
PORT = os.environ.get('NESTML_SERVER_PORT', '5005')

BUILD = os.environ.get('NESTML_BUILD_PATH', '/tmp/nestml_build')
MODELS = os.environ.get('NESTML_MODELS_PATH', '/tmp/nestml_models')
NEST = os.environ.get('NESTML_NEST_PATH', '/home/spreizer/opt/nest-nestml')

EXCEPTION_ERROR_STATUS = 400


__all__ = [
    'app'
]

app = Flask(__name__)
CORS(app)

# ----------------------
# Routes for the server
# ----------------------

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'nest': nest.__version__,
        'nestml': pynestml.__version__,
    })

@app.route('/install', methods=['POST'])
@cross_origin()
def install():
    data = request.get_json()
    response = do_install(data)
    return jsonify(response)


# ----------------------
# Helpers for the server
# ----------------------

def get_or_error(func):
    """ Wrapper to get data and status.
    """
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            for line in traceback.format_exception(*sys.exc_info()):
                print(line, flush=True)
            abort(Response(str(e), EXCEPTION_ERROR_STATUS))
    return func_wrapper

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

# ----------------------
# Executions for the server
# ----------------------

@get_or_error
def do_install(data):
    """ Install nestml models.
    """
    models = data.get('models', [])
    status = {'INITIALIZED': [], 'WRITTEN': [], 'BUILT': [], 'INSTALLED':[]}

    # Remove all nestml model files.
    clear_folder(MODELS)

    # Write nestml models in files.
    for model in models:
        model_name = model['name']
        status['INITIALIZED'].append(model_name)
        model_script = model['script']
        filename = os.path.join(MODELS, model_name)
        with open(filename + '.nestml', 'w') as f:
            f.write(model_script)

    # Check if models are built.
    for file in os.listdir(MODELS):
        if file.endswith('.nestml'):
            model_name, _ = file.split('.')
            status['WRITTEN'].append(model_name)

    # Remove all build files.
    clear_folder(BUILD)

    # Build nestml models.
    module_name = data.get('module_name', 'nestmlmodule')
    to_nest(MODELS, BUILD, module_name=module_name)

    # Check if models are built.
    for file in os.listdir(BUILD):
        if file.endswith('.cpp'):
            model_name, _ = file.split('.')
            status['BUILT'].append(model_name)

    # Install nestml models.
    install_nest(BUILD, NEST)

    # Check if models are installed in NEST.
    # nest.ResetKernel()
    # nest.Install(module_name)
    # kernel_status = nest.GetKernelStatus()
    # for model in status.keys():
    #     if model in kernel_status['node_models'] or model in kernel_status['synapse_models']:
    #         status['INSTALLED'].append(model_name)

    return {'status': status}


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
