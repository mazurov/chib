#!/usr/bin/env ipython

""" Print MC fit parameters """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30),
           (18, 30)]

BINNINGS = [[(6, 8), (8, 10), (10, 12), (12, 14)], [(14, 18), (18, 22), (22, 30), (18, 30)]]
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
# ============================================================================
renderer = pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")
# ============================================================================
# Extract efficencies
db = db.DB(ups="ups_1cb")

print renderer.render_name("upsfit-head", {})
for BINNING in BINNINGS:
    # ============================================================================
    alignment = "rrr" * (len(BINNING))
    # ============================================================================
    bins = ""
    for bin in BINNING:
        bins += " & & \multicolumn{2}{c}{%s}" % (
                "$%s < p_T(\Upsilon) < %s \gevc$" % bin if bin[1] else "$p_T(\Upsilon)> %d \gevc$" % bin[0]
            )
    years = ""
    lines = ""

    i = 3
    for bin in BINNING:
        years += " && \sqs = 7 \\tev & \sqs = 8\\tev"
        lines += "\cmidrule{%d-%d}" % (i, i+1)
        i += 3

    # ============================================================================
    N = ["", "", ""]
    # N1_2 = ""
    B = ""
    mu = ""
    dm2 = ""
    dm3 = ""
    sigma = ""
    al = ""
    # ar = ""
    n = ""
    tau = ""
    c0 = ""
    c1 = ""

    for bin in BINNING:
        for year in ("2011", "2012"):
            prefix = "&" if year == "2012" else "&&"
            fit = db.upsfit(year, bin)
            for iy in range(3):
                key = "N%dS" % (iy + 1)
                N[iy] += prefix + "%s" % utils.latex_ve_pair(fit[key])
            # N1_2 += " & %s" % utils.latex_ve_pair(fit["N1S_1"])
            B +=  prefix + "%s" % utils.latex_ve_pair(fit["B"])

            mu +=  prefix + "%s" % utils.latex_ve_pair(VE(str(fit["m1s"])) * 1000)
            dm2 +=  prefix + "%s" % utils.latex_ve_pair(VE(str(fit["dm2s"])) * 1000)
            dm3 +=  prefix + "%s" % utils.latex_ve_pair(VE(str(fit["dm3s"])) * 1000)
            sigma +=  prefix + "%s" % utils.latex_ve_pair(VE(str(fit["sigma"])) * 1000)

            al +=  prefix + "%s" % fit["alphaL"]
            # ar += "%s" % fit["alphaR"]
            n +=  prefix + "%s" % utils.latex_ve_pair(fit["n"])

            tau +=  prefix + "%s" % utils.latex_ve_pair(fit["tau_bg"])
            c0 +=  prefix + "%s" % utils.latex_ve_pair(fit["phi1_bg"])
            c1 +=  prefix + "%s" % utils.latex_ve_pair(fit["phi2_bg"])

    context = {
        "year": year,
        "e": "7" if year == "2011" else "8",
        "alignment": alignment,
        "cols": 3*len(BINNING),
        "years": years,
        "lines": lines,
        "bins": bins,
        # "N1_2": N1_2,
        "B": B,
        "mu": mu,
        "dm2": dm2,
        "dm3": dm3,
        "sigma": sigma,
        "al": al,
        # "ar": ar,
        "n": n,
        "tau": tau,
        "c0": c0,
        "c1": c1,
    }

    for iy in range(3):
        context["N%d" % (iy + 1)] = N[iy]

    print ("\subtable[]{" if len(BINNINGS) > 1 else "")
    print renderer.render_name("upsfit", context)
    print ("}" if len(BINNINGS) > 1 else "")
print renderer.render_name("upsfit-foot", context)
