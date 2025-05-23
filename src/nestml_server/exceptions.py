#!/usr/bin/env python
# exceptions.py

import sys # noqa
import traceback # noqa

# from pynestml.utils.logger import Logger


__all__ = [
    "ErrorHandler",
    "call_or_error",
]

EXCEPTION_ERROR_STATUS = 400

class ErrorHandler(Exception):
    status_code = 400
    lineno = -1

    def __init__(self, message: str, lineno: int = None, status_code: int = None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if lineno is not None:
            self.lineno = lineno
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        if self.lineno != -1:
            rv["lineNumber"] = self.lineno
        return rv


def call_or_error(func):
    """Wrapper to call a function."""

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            # log = Logger.get_log()
            # print('Logger', log)

            error_class = err.__class__.__name__
            detail = err.args[0]
            lineno = get_lineno(err, -1)

        # for line in traceback.format_exception(*sys.exc_info()):
        #     print(line, flush=True)

        if lineno == -1:
            message = "%s: %s" % (error_class, detail)
        else:
            message = "%s at line %d: %s" % (error_class, lineno, detail)

        raise ErrorHandler(message, lineno)

    return func_wrapper

def get_lineno(err, tb_idx):
    lineno = -1
    if hasattr(err, "lineno") and err.lineno is not None:
        lineno = err.lineno
    else:
        tb = sys.exc_info()[2]
        # if hasattr(tb, "tb_lineno") and tb.tb_lineno is not None:
        #     lineno = tb.tb_lineno
        # else:
        lineno = traceback.extract_tb(tb)[tb_idx][1]
    return lineno
