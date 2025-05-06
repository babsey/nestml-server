from importlib import metadata as _metadata # noqa

__version__ = _metadata.version("nestml-server")
del _metadata