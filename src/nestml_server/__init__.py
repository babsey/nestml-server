from importlib import metadata  # noqa

try:
    __version__ = metadata.version("nestml-server")
    del metadata
except:
    pass
