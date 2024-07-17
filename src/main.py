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

MAJOR_VERSION = int(pynestml.__version__.split(".")[0])

HOST = os.environ.get("NESTML_SERVER_HOST", "127.0.0.1")
PORT = os.environ.get("NESTML_SERVER_PORT", "52426")

MODULES_PATH = os.environ.get("NESTML_MODULES_PATH", "/tmp/nestmlmodules")
os.makedirs(MODULES_PATH, exist_ok=True)

EXCEPTION_ERROR_STATUS = 400


__all__ = ["app"]

app = Flask(__name__)
CORS(app)

# ----------------------
# Routes for the server
# ----------------------


@app.route("/", methods=["GET"])
def index():
    return jsonify({"nest": nest.__version__, "nestml": pynestml.__version__})


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


@app.route("/models", methods=["GET"])
def get_all_models():
    modules = do_get_modules()
    models = {}
    for module in modules:
        models[module] = do_get_models(module)

    return jsonify(models)


@app.route("/module/<module>/installed", methods=["GET"])
def get_installed(module):
    models = do_get_installed(module)
    return jsonify(models)


@app.route("/module/<module>/models", methods=["GET"])
def get_models(module):
    models = do_get_models(module)
    return jsonify(models)


@app.route("/module/<module>/model/<model_name>", methods=["GET"])
def get_model(module, model_name):
    model_script = do_get_model_script(module, model_name)
    return jsonify({"script": model_script})


@app.route("/modules", methods=["GET"])
def get_modules():
    modules = do_get_modules()
    return jsonify(modules)


# ----------------------
# Helpers for the server
# ----------------------


def clean_param(param):
    keys = [k for k, v in param.items() if v == None]
    for key in keys:
        del param[key]


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


def get_models_path(module_name):
    return os.path.join(MODULES_PATH, module_name, "models")


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


def get_module_path(module_name):
    return os.path.join(MODULES_PATH, module_name, "module")


def try_or_pass(value):
    try:
        return value()
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
        models_path = get_models_path(module_name)
        module_path = get_module_path(module_name)

        for path in [models_path, module_path]:
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
        for file in os.listdir(models_path):
            if file.endswith(".nestml"):
                model_name, _ = file.split(".")
                status["WRITTEN"].append(model_name)

        # print(status["WRITTEN"])

        # Generate nest model components in a nestml module.
        generate_nest_target(
            input_path=models_path,
            install_path=MODULES_PATH,
            module_name=module_name,
            target_path=module_path,
        )

        # Check if models are generated.
        for file in os.listdir(module_path):
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
def do_get_installed(module_name):
    filenames = os.listdir(get_module_path(module_name))
    models = filter(lambda filename: (not filename.startswith(module_name) and filename.endswith(".cpp")), filenames)
    models = map(lambda model: model.split(".")[0], models)
    return list(models)


@get_or_error
def do_get_models(module_name):
    filenames = os.listdir(get_models_path(module_name))
    models = filter(lambda filename: filename.endswith(".nestml"), filenames)
    models = map(lambda model: model.split(".")[0], models)
    return list(models)


@get_or_error
def do_get_model_script(module_name, model_name):
    filename = os.path.join(get_models_path(module_name), model_name)
    with open(filename + ".nestml", "r") as f:
        script = f.read()
    return script


@get_or_error
def do_get_modules():
    filenames = os.listdir(MODULES_PATH)
    modules = filter(lambda filename: filename.endswith(".so"), filenames)
    modules = map(lambda filename: filename.split(".")[0], modules)
    return list(modules)


@get_or_error
def do_get_params(data):
    init_predefined()

    if MAJOR_VERSION >= 8:
        model = ModelParser.parse_model(data["script"])
    else:
        element_type = data.get("element_type", "neuron")
        model = getattr(ModelParser, "parse_" + element_type)(data["script"])

    params = []
    if model:
        declarations = model.get_parameters_blocks()[0].declarations
        for declaration in declarations:
            param = {}

            param["id"] = try_or_pass(lambda: declaration.variables[0].name)
            param["label"] = try_or_pass(lambda: declaration.print_comment().strip())

            expression = declaration.expression
            value = 1

            if expression.__str__().startswith("-"):
                expression = expression.expression
                value = -1

            param["value"] = value * try_or_pass(lambda: expression.numeric_literal)

            if expression.has_unit():
                param["unit"] = try_or_pass(lambda: expression.get_units()[0].name)

            clean_param(param)
            params.append(param)

    return {"params": params}


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
