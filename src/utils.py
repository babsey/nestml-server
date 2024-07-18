#!/usr/bin/env python3

import sys

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response
import traceback

EXCEPTION_ERROR_STATUS = 400

__all__ = [
    "get_or_error",
    "try_or_pass",
]


def get_or_error(func):
    """Wrapper to get data and status."""

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            for line in traceback.format_exception(*sys.exc_info()):
                print(line, flush=True)
            abort(Response(str(e), EXCEPTION_ERROR_STATUS))

    return func_wrapper


def try_or_pass(value):
    try:
        return value()
    except:
        pass
