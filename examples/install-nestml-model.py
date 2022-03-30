from pynestml.frontend.pynestml_frontend import to_nest, install_nest

MODELS = '/home/spreizer/Projects/nestml-server/models'
BUILD = '/tmp/nestml/build'
NEST = '/home/spreizer/opt/nest-nestml'

to_nest(MODELS, BUILD, module_name='nestmlmodule')
install_nest(BUILD, NEST)
