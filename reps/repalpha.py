#!/usr/bin/env ipython

""" Find alpha parameter for b1 and b2 states """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30),
           (18, 30)]
# ============================================================================
from lib import utils
from lib import pdg
from lib import db

import os
import sys

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'ext')]
# ============================================================================
import pystache
import shelve
# ============================================================================
renderer = pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")
# ============================================================================
# Extract efficencies
db = db.DB()
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================
sigmas = ""
eff = ["", ""]
ratio = ["", ""]
frac = ["", ""]
# br = [pdg.BR21_Y1S / pdg.BR11_Y1S, pdg.BR22_Y1S / pdg.BR12_Y1S]
for bin in BINNING:
    sigmas += " & %s" % utils.latex_ve(db.crossb2b1(bin))
    for ip in range(2):
        e = db.eff(bin=bin, np=ip+1, nb=2) / db.eff(bin=bin, np=ip+1, nb=1)
        r = db.ratiob2b1(bin, ip+1)
        a = db.alphab1(bin, ip+1)
        eff[ip] += " & %s" % utils.latex_ve(e)
        ratio[ip] += " & %s" % utils.latex_ve(r)
        frac[ip] += " & %s" % utils.latex_ve(a)
# ============================================================================

context = {
    "alignment": alignment,
    "nbins": len(BINNING),
    "bins": bins,
    "sigmas": sigmas,
    "eff1": eff[0],
    "eff2": eff[1],
    "ratio1": ratio[0],
    "ratio2": ratio[1],
    "frac1": frac[0],
    "frac2": frac[1],
}
print renderer.render_name("alpha", context)
