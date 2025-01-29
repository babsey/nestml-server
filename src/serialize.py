#!/usr/bin/env python
# serialize.py

import pynestml

from pynestml.frontend.pynestml_frontend import init_predefined
from pynestml.utils.model_parser import ModelParser

from .exceptions import call_or_error

MAJOR_VERSION = int(pynestml.__version__.split(".")[0])


@call_or_error
def do_parse_model(model_script: str, element_type: str = "neuron"):
    init_predefined()

    if MAJOR_VERSION >= 8:
        model = ModelParser.parse_model(model_script)
    else:
        model = getattr(ModelParser, "parse_" + element_type)(model_script)

    return model
