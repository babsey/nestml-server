#!/usr/bin/env python3

import os
import sys
import shutil

from flask import abort, Flask, jsonify, request
from flask_cors import CORS

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response
import traceback

import nest
import pynestml

from pynestml.frontend.pynestml_frontend import init_predefined, generate_nest_target
from pynestml.utils.model_parser import ModelParser


HOST = os.environ.get("NESTML_SERVER_HOST", "127.0.0.1")
PORT = os.environ.get("NESTML_SERVER_PORT", "52426")

MODELS_PATH = os.environ.get("NESTML_MODELS_PATH", "/tmp/nestml_models")
TARGETS_PATH = os.environ.get("NESTML_TARGETS_PATH", "/tmp/nestml_targets")
for path in [MODELS_PATH, TARGETS_PATH]:
    os.makedirs(path, exist_ok=True)

EXCEPTION_ERROR_STATUS = 400


__all__ = ["app"]

app = Flask(__name__)
CORS(app)

# ----------------------
# Routes for the server
# ----------------------


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "nest": nest.__version__,
            "nestml": pynestml.__version__,
        }
    )


@app.route("/generateModels", methods=["POST"])
def generate_models():
    data = request.get_json()
    response = do_generate_models(data)
    return jsonify(response)


@app.route("/getParams", methods=["POST"])
def get_params():
    data = request.get_json()
    response = do_get_params(data)
    return jsonify(response)


@app.route("/models", methods=["GET", "POST"])
def get_models():
    if request.is_json:
        data = request.get_json()
        module = data.get("module", "nestmlmodule")
    else:
        module = "nestmlmodule"

    filenames = os.listdir(os.path.join(TARGETS_PATH, module))
    models = filter(lambda filename: (not filename.startswith(module) and filename.endswith(".cpp")), filenames)
    models = map(lambda model: model.split(".")[0], models)
    return jsonify(list(models))


@app.route("/modules", methods=["GET"])
def get_modules():
    filenames = os.listdir(TARGETS_PATH)
    modules = filter(lambda filename: filename.endswith("module"), filenames)
    return jsonify(list(modules))


# ----------------------
# Helpers for the server
# ----------------------


def get_or_error(func):
    """Wrapper to get data and status."""

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            for line in traceback.format_exception(*sys.exc_info()):
                print(line, flush=True)
            abort(Response(str(e), EXCEPTION_ERROR_STATUS))

    return func_wrapper


def clear_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def try_or_pass(dict, key, value):
    try:
        dict[key] = value()
    except:
        pass


# -------------------------
# Executions for the server
# -------------------------


@get_or_error
def do_generate_models(data):
    """Generate nestml models."""
    module_name = data.get("module_name", "nestmlmodule")
    if type(module_name) == list:
        module_name = module_name[0]

    models = data.get("models", [])
    status = {"INITIALIZED": [], "WRITTEN": [], "BUILT": [], "INSTALLED": []}

    if len(models) > 0:
        models_path = os.path.join(MODELS_PATH, module_name)
        targets_path = os.path.join(TARGETS_PATH, module_name)

        for path in [models_path, targets_path]:
            os.makedirs(path, exist_ok=True)
            clear_dir(path)

        # Write nestml models in files.
        for model in models:
            model_name = model["name"]
            model_script = model["script"]
            status["INITIALIZED"].append(model_name)

            filename = os.path.join(models_path, model_name)
            with open(filename + ".nestml", "w") as f:
                f.write(model_script)

        # print(status["INITIALIZED"])

        # Check if models are built.
        for file in os.listdir(MODELS_PATH):
            if file.endswith(".nestml"):
                model_name, _ = file.split(".")
                status["WRITTEN"].append(model_name)

        # print(status["WRITTEN"])

        # Generate nestml model components.
        generate_nest_target(input_path=models_path, target_path=targets_path, module_name=module_name)

        # Check if models are generated.
        for file in os.listdir(targets_path):
            if file.endswith(".cpp"):
                model_name, _ = file.split(".")
                status["BUILT"].append(model_name)

        # print(status["BUILT"])

        # Check if models are installed in NEST.
        nest.ResetKernel()
        nest.Install(module_name)
        kernel_status = nest.GetKernelStatus()
        for model in status["BUILT"]:
            if model in kernel_status["node_models"] or model in kernel_status["synapse_models"]:
                status["INSTALLED"].append(model)

        # print(status["INSTALLED"])

    return {"status": status}


@get_or_error
def do_get_params(data):
    init_predefined()

    element_type = data.get("element_type", "neuron")
    model_parsed = getattr(ModelParser, "parse_" + element_type)(data["script"])

    params = []
    if model_parsed:
        model_parameters_declarations = model_parsed.get_parameters_blocks()[0].declarations
        for model_parameters_declaration in model_parameters_declarations:
            param = {}

            try_or_pass(param, "id", lambda: model_parameters_declaration.variables[0].name)
            try_or_pass(param, "label", lambda: model_parameters_declaration.comment[0][1:])

            # Get values.
            try_or_pass(param, "value", lambda: model_parameters_declaration.expression.numeric_literal)
            try_or_pass(param, "value", lambda: model_parameters_declaration.expression.expression.numeric_literal)

            if model_parameters_declaration.data_type.is_unit_type():
                try_or_pass(param, "unit", lambda: model_parameters_declaration.data_type.unit_type.unit)

            params.append(param)

    return {"params": params}


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
