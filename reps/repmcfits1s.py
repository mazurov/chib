#!/usr/bin/env ipython

""" Print MC fit parameters """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30),
           (18, 30)]
# BINNING = [(18, 22), (22,30)]
# ============================================================================
from lib import utils
from lib import db

import os
import sys

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'ext')]
# ============================================================================
import pystache
# ============================================================================
renderer = pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")
# ============================================================================
# Extract efficencies
db = db.DB(mc="mc_1s_tr")
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================

for ip in range(3):
    N = ["", ""]
    B = ["", ""]
    mean = ["", ""]
    sigma = ["", ""]
    a = ["", ""]
    n = ["", ""]
    for bin in BINNING:
        for ib in range(2):
            fit = db.mcfit(bin, ip + 1, ib + 1)
            N[ib] += " & %s" % utils.latex_ve_pair(fit["N"])
            B[ib] += " & %s" % utils.latex_ve_pair(fit["B"])
            mean[ib] += " & %s" % utils.latex_ve(VE(str(fit["mean"]))*1000)
            sigma[ib] += " & %s" % utils.latex_ve(VE(str(fit["sigma"]))*1000)
            a[ib] += " & %s" % utils.latex_ve_pair(
                fit["a" if "a" in fit else "ar"])
            n[ib] += " & %s" % utils.latex_ve_pair(
                fit["n" if "n" in fit else "nr"])
    context = {
        "p": ip+1,
        "alignment": alignment,
        "nbins": len(BINNING),
        "bins": bins,
    }

    for ib in range(2):
        context["N%d" % (ib + 1)] = N[ib]
        context["B%d" % (ib + 1)] = B[ib]
        context["mean%d" % (ib + 1)] = mean[ib]
        context["sigma%d" % (ib + 1)] = sigma[ib]
    context["a"] = a[0]
    context["n"] = n[0]

    print renderer.render_name("mcfit1s", context)
