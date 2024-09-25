#!/usr/bin/env python3

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from .helpers import (
    do_generate_models,
    do_get_json,
    do_get_params,
    do_get_states,
    do_get_versions,
    do_parse_model,
)
from .utils import (
    do_get_installed,
    do_get_model_script,
    do_get_models,
    do_get_modules,
)

HOST = os.environ.get("NESTML_SERVER_HOST", "127.0.0.1")
PORT = os.environ.get("NESTML_SERVER_PORT", "52426")

__all__ = ["app"]

app = Flask(__name__)
CORS(app)

# ----------------------
# Routes for the server
# ----------------------


@app.route("/", methods=["GET"])
def index():
    versions = do_get_versions()
    return jsonify(versions)


@app.route("/generateModels", methods=["POST"])
def generate_models():
    data = request.get_json()
    response = do_generate_models(data)
    return jsonify(response)


@app.route("/getJSON", methods=["POST"])
def generate_json():
    data = request.get_json()
    response = do_get_json(data)
    return jsonify(response)


@app.route("/getSpecs", methods=["POST"])
def get_states():
    data = request.get_json()
    model = do_parse_model(data)
    params = do_get_params(model)

    try:
        states = do_get_states(model)
    except:
        states = []

    return jsonify({"params": params, "states": states})


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


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
