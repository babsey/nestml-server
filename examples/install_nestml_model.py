from pynestml.frontend.pynestml_frontend import generate_nest_target

MODELS_PATH = "${PWD}/../models"
TARGETS_PATH = "/tmp/nestml_targets"
module_name = "nestmlmodule"

generate_nest_target(MODELS_PATH, TARGETS_PATH, module_name=module_name)
