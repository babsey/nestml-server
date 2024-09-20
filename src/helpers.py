#!/usr/bin/env python3

import os
import shutil

import nest
import pynestml

from pynestml.frontend.pynestml_frontend import init_predefined, generate_nest_target
from pynestml.utils.model_parser import ModelParser

from .generators import get_json_from_existed_neuron
from .utils import get_or_error, try_or_pass

MODULES_PATH = os.environ.get("NESTML_MODULES_PATH", "/tmp/nestmlmodules")
os.makedirs(MODULES_PATH, exist_ok=True)

MAJOR_VERSION = int(pynestml.__version__.split(".")[0])

__all__ = [
    "do_generate_models",
    "do_get_installed",
    "do_get_json",
    "do_get_model_script",
    "do_get_models",
    "do_get_modules",
    "do_get_params",
    "do_get_versions",
]

models_dirname = "models"
module_dirname = "module"


def clean_dict(d):
    keys = [k for k, v in d.items() if v == None]
    for key in keys:
        del d[key]


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


def get_module_path(module_name):
    return os.path.join(MODULES_PATH, module_name)


def init_module_path(module_name):
    module_path = get_module_path(module_name)
    for dirname in [models_dirname, module_dirname]:
        dir_path = os.path.join(module_path, dirname)
        os.makedirs(dir_path, exist_ok=True)
        clear_dir(dir_path)
    return module_path


@get_or_error
def do_generate_models(data):
    """Generate nestml models."""
    module_name = data.get("module_name", "nestmlmodule")
    if type(module_name) == list:
        module_name = module_name[0]

    models = data.get("models", [])
    status = {"INITIALIZED": [], "WRITTEN": [], "BUILT": [], "INSTALLED": []}
    init_predefined()

    if len(models) > 0:
        module_path = init_module_path(module_name)

        # Write nestml models in files.
        for model in models:
            model_name = model["name"]
            model_script = model["script"]
            status["INITIALIZED"].append(model_name)

            model_parsed = ModelParser.parse_model(model_script)
            assert model_parsed.name == model["name"]

            filename = os.path.join(module_path, models_dirname, model_name)
            with open(filename + ".nestml", "w") as f:
                f.write(model_script)

        # print(status["INITIALIZED"])

        # Check if models are built.
        for file in os.listdir(os.path.join(module_path, models_dirname)):
            if file.endswith(".nestml"):
                model_name, _ = file.split(".")
                status["WRITTEN"].append(model_name)

        # print(status["WRITTEN"])

        # Generate nest model components in a nestml module.
        generate_nest_target(
            input_path=os.path.join(module_path, models_dirname),
            install_path=MODULES_PATH,
            module_name=module_name,
            target_path=os.path.join(module_path, module_dirname),
        )

        # Check if models are generated.
        for file in os.listdir(os.path.join(module_path, module_dirname)):
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
    filenames = os.listdir(os.path.join(get_module_path(module_name), module_dirname))
    models = filter(lambda filename: (not filename.startswith(module_name) and filename.endswith(".cpp")), filenames)
    models = map(lambda model: model.split(".")[0], models)
    return list(models)


@get_or_error
def do_get_json(data):
    model_name = data["model_name"]
    data_json = get_json_from_existed_neuron(model_name)
    return data_json


@get_or_error
def do_get_models(module_name):
    filenames = os.listdir(os.path.join(get_module_path(module_name), models_dirname))
    models = filter(lambda filename: filename.endswith(".nestml"), filenames)
    models = map(lambda model: model.split(".")[0], models)
    return list(models)


@get_or_error
def do_get_model_script(module_name, model_name):
    filename = os.path.join(get_module_path(module_name), models_dirname, model_name)
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
def do_get_params(model):
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

            clean_dict(param)
            params.append(param)

    return params


@get_or_error
def do_get_states(model):
    states = []

    if model:
        declarations = model.get_state_blocks()[0].declarations
        for declaration in declarations:
            state = {}

            state["id"] = try_or_pass(lambda: declaration.variables[0].name)
            state["label"] = try_or_pass(lambda: declaration.print_comment().strip())

            data_type = declaration.data_type.__str__()
            expression = declaration.expression

            if data_type == "boolean":
                state["value"] = bool(expression.__str__())
            else:
                value = 1
                if expression.__str__().startswith("-"):
                    expression = expression.expression
                    value = -1

                state["value"] = value * try_or_pass(lambda: expression.numeric_literal)

                if expression.has_unit():
                    state["unit"] = try_or_pass(lambda: expression.get_units()[0].name)

            # print(state)
            clean_dict(state)
            states.append(state)

    return states


@get_or_error
def do_get_versions():
    return {"nest": nest.__version__, "nestml": pynestml.__version__}


@get_or_error
def do_parse_model(data):
    init_predefined()

    if MAJOR_VERSION >= 8:
        model = ModelParser.parse_model(data["script"])
    else:
        element_type = data.get("element_type", "neuron")
        model = getattr(ModelParser, "parse_" + element_type)(data["script"])

    return model
