#!/usr/bin/env python
# utils.py

import os
import shutil


__all__ = [
    "try_or_pass",
]

models_dirname = "models"
module_dirname = "module"

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
    return os.path.join(MODULES_PATH, module_name)


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


