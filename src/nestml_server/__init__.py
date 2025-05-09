from importlib import metadata  # noqa

try:
    __version__ = metadata.version("nestml-server")
except metadata.PackageNotFoundError:
    pass

del metadata
