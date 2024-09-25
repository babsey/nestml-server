#!/usr/bin/env python3

import os
import shutil
import sys

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response
import traceback

__all__ = [
    "get_or_error",
    "try_or_pass",
]

models_dirname = "models"
module_dirname = "module"

EXCEPTION_ERROR_STATUS = 400
MODULES_PATH = os.environ.get("NESTML_MODULES_PATH", "/tmp/nestmlmodules")
os.makedirs(MODULES_PATH, exist_ok=True)


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
    return os.path.join(module_name)


def get_or_error(func):
    """Wrapper to get data and status."""

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if len(str(e)) == 0:
                e = traceback.format_exception(*sys.exc_info())[-1]
            print(e)
            abort(EXCEPTION_ERROR_STATUS, str(e))

    return func_wrapper


def init_module_path(module_name):
    module_path = get_module_path(module_name)
    for dirname in [models_dirname, module_dirname]:
        dir_path = os.path.join(module_path, dirname)
        os.makedirs(dir_path, exist_ok=True)
        clear_dir(dir_path)
    return module_path


def try_or_pass(value):
    try:
        return value()
    except:
        pass


@get_or_error
def do_get_installed(module_name):
    filenames = os.listdir(os.path.join(get_module_path(module_name), module_dirname))
    models = filter(lambda filename: (not filename.startswith(module_name) and filename.endswith(".cpp")), filenames)
    models = map(lambda model: model.split(".")[0], models)
    return list(models)


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
