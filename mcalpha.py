#!/usr/bin/env ipython


""" Find alpha parameter for b1 and b2 states """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
DEFAULT_SIGMA = VE(1, 0.05 ** 2)
SIGMAS = {
    (6, 8): VE(1.775, 0.175 ** 2),
    (8, 10): VE(1.5, 0.1 ** 2),
    (10, 12): VE(1.3, 0.1 ** 2),
    (12, 14): VE(1.15, 0.05 ** 2),
    (14, 18): VE(1.05, 0.05 ** 2),
    (18, 22): VE(0.95, 0.05 ** 2),
    (12, 30): VE(0.85, 0.05 ** 2),
    (18, 30): VE(0.9, 0.1 ** 2)
}

BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30),
           (18, 30)]
# ============================================================================
from lib import utils
from lib import pdg
from lib import db

import os
import sys

db = db.DB()
for bin in BINNING:
    sigmas += " & "
    if bin in SIGMAS:
        sigmas += "%s" % utils.latex_ve(SIGMAS[bin])
    else:
        sigmas += "%s" % utils.latex_ve(DEFAULT_SIGMA)
    for ip in range(2):
        e = db.eff(bin=bin, np=ip+1, nb=2) / db.eff(bin=bin, np=ip+1, nb=1)
        sigma = SIGMAS[bin] if bin in SIGMAS else DEFAULT_SIGMA
        r = sigma*br[ip]*e
        eff[ip] += " & %s" % utils.latex_ve(e)
        ratio[ip] += " & %s" % utils.latex_ve(r)
        frac[ip] += " & %s" % utils.latex_ve(1.0/(r+1))
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
