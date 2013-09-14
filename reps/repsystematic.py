#!/usr/bin/env ipython

# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNINGS = [
    [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)],
    [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 30)],
    [(12, 14), (14, 18), (18, 30)]
]

# ============================================================================
from lib import utils

import os
import sys
import shelve
from IPython import embed as shell  # noqa

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'ext')]
# ============================================================================
import pystache
# ============================================================================
renderer = pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")
# ============================================================================

reference = shelve.open("data/chib1s_massall.db", "r")["2012"]


def values(ip, binning, dbname, year="2012"):
    db = shelve.open("data/%s.db" % dbname)[year]
    key = "N%dP" % (ip + 1)

    result = ""
    for bin in binning:
        ref = VE(str(reference[bin][key]))
        val = VE(str(db[bin][key]))
        p = (val/ref - 1)*100
        result += " & % s" % utils.latex_ve(p)
    return result

for ip in range(3):
    nominal = ""
    binning = BINNINGS[ip]

    alignment = "c" * (len(binning))
    bins = ""
    for bin in binning:
        fit = reference[bin]
        bins += " & %d --- %d" % bin
        nominal += " & %s" % utils.latex_ve_pair(
            VE(str(fit["N%dP" % (ip + 1)])))

    context = {
        "N": ip + 1,
        "alignment": alignment,
        "bins": bins,
        "nbins": len(binning),
        "scale": 1 if ip != 0 else 0.8,
        "nominal": nominal,
        "mu_min": values(ip, binning, "chib1s_massmin"),
        "mu_max": values(ip, binning, "chib1s_massmax")
    }
    print renderer.render_name("systematic", context)
