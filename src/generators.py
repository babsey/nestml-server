#!/usr/bin/env python3

import os
import pynestml
import json

from pynestml.codegeneration.nest_desktop_code_generator import NESTDesktopCodeGenerator
from pynestml.frontend.pynestml_frontend import init_predefined
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


NESTML_ROOT = os.path.dirname(os.path.dirname(pynestml.__file__))

__all__ = ["get_json_from_existed_neuron"]

init_predefined()

visitor = ASTSymbolTableVisitor()
code_generator = NESTDesktopCodeGenerator(
    {
        "templates": {
            "path": os.path.join(NESTML_ROOT, "pynestml", "codegeneration", "resources_nest_desktop"),
            "model_templates": {
                "neuron": ["@NEURON_NAME@.json.jinja2"],
            },
        },
    }
)
neuron_templ = code_generator._model_templates["neuron"][0]


def generate_json_from_script(script: str):
    model = ModelParser.parse_model(script)

    visitor.visit_model(model)
    visitor.traverse_model(model)

    neuron_namespace = code_generator._get_neuron_model_namespace(model)
    neuron_data = neuron_templ.render(neuron_namespace)
    neuron_json = json.loads(neuron_data)

    return neuron_json


def get_json_from_existed_neuron(neuron):
    filepath = os.path.join(NESTML_ROOT, "models", "neurons", neuron + "_neuron.nestml")
    with open(filepath, "r") as f:
        lines = f.readlines()
    script = "".join(lines)

    return generate_json_from_script(script)


if __name__ == "__main__":

    print(get_json_from_existed_neuron("iaf_psc_alpha"))
