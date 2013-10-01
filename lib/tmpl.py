import os
import sys
import types
from lib import utils

from AnalysisPython.PyRoUts import VE

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'ext')]

import pystache

def renderer():
    return pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")

def col(val, bold=False):
    result = " & "
    if bold:
        result += "\\textbf{"
    result += str(val)
    if bold:
        result += "}"
    return result


def bins(lst):
    sbins = ""
    for bin in lst:
        sbins += " & %d --- %d" % bin

    result = {
        "bins": sbins,
        "ncols": len(lst),
        "alignment": "c" * len(lst)
    }
    return result

def mulicolumn(v, digits=2):
    fmt = "\multicolumn{2}{c}{%%.%df}" % digits
    return fmt % v

def output(year, fit, key, scale=1, digits=2, var=False):
    result = " && " if year == "2011" else " & "

    if key in fit:
        v = fit[key]
        if var or isinstance(v, types.TupleType):
            result += utils.latex_ve(VE(str(v)) * scale)
        elif year == "2011":
            result += mulicolumn(v*scale, digits)
        else:
            return ""
    else:
        result += " - "
    return result