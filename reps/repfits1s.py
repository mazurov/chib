#!/usr/bin/env ipython

""" Print MC fit parameters """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30),
           (18, 30)]
BINNINGS = [[(6, 8), (8, 10)]]
BINNINGS = [[(14, None)]]

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
db = db.DB(chib="chib1s_dm")
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================
print renderer.render_name("fits1s-head", {})
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


    N = ["", "", ""]
    B = ""
    mean = ""
    dm = ["", ""]
    dmb2b1 = ["", "", ""]
    frac = ["", "", ""]
    a = ["", "", ""]
    n = ["", "", ""]
    sigma = ""
    sigmab2b1 = ""
    sfrac = ["", ""]

    tau = ""
    phi = ["","","","",""]

    chi2 = ""
    for bin in BINNING:
        for year in ["2011", "2012"]:
            fit = db.fit(year, bin)
            prefix = " & " if year == "2012" else " && "
            for ip in range(3):
                key = "N%dP" % (ip + 1)
                if key in fit:
                    N[ip] += prefix + " %s" % utils.latex_ve_pair(fit[key])
                else:
                    N[ip] += prefix + " - "

                if ip == 0:
                    key = "mean_b1_1p"
                    mean += prefix + " %s" % utils.latex_ve(VE(str(fit[key])) * 1000)
                else:
                    key = "dm_b1%dp_b11p" % (ip + 1)
                    if key in fit:
                        dm[ip-1] += prefix + " %s" % utils.latex_ve(VE(str(fit[key])) * 1000)
                    else:
                        dm[ip-1] += prefix + " - "

                key = "dmb2b1_%dp" % (ip + 1)
                if key in fit:
                    dmb2b1[ip] += prefix + " %s" % utils.latex_ve(
                        VE(str(fit[key])) * 1000)
                else:
                    dmb2b1[ip] += prefix + " - "
                if ip > 0:
                    key = "sfrac%dp1p" % (ip + 1)
                    if key in fit:
                        sfrac[ip - 1] += prefix + " %s" % utils.latex_ve_pair(fit[key])
                    else:
                        sfrac[ip - 1] += prefix + " - "

                key = "frac%d" % (ip + 1)
                if key in fit:
                    frac[ip] += prefix + " %s" % utils.latex_ve(VE(str(fit[key])))
                else:
                    frac[ip] += prefix + " - "

                key = "a%d" % (ip + 1)
                if key in fit:
                    a[ip] += prefix + " %s" % utils.latex_ve(VE(str(fit[key])))
                else:
                    a[ip] += prefix + " - "

                key = "n%d" % (ip + 1)
                if key in fit:
                    n[ip] += prefix + " %s" % utils.latex_ve(VE(str(fit[key])))
                else:
                    n[ip] += prefix + " - "

            sigma += prefix + " %s" % utils.latex_ve(VE(str(fit["sigma_b1_1p"])) * 1000)
            sigmab2b1 += prefix + " %s" % utils.latex_ve(VE(str(fit["sdiffb2b1"])))
            B += prefix + " %s" % utils.latex_ve_pair(fit["B"])

            tau += prefix + " %s" % utils.latex_ve_pair(fit["exp_tau"])
            for iphi in range(5):
                key = "poly_phi%d" % (iphi+1)
                if key in fit:
                    phi[iphi] += prefix + " %s" % utils.latex_ve(VE(str(fit[key])))
                else:
                    phi[iphi] += prefix + " - "
            chi2 += prefix + " %s" % utils.latex_ve_pair(fit["chi2"])
        context = {
            "alignment": alignment,
            "cols": 3*len(BINNING),
            "years": years,
            "lines": lines,
            "bins": bins,
            "B": B,
            "sigma": sigma,
            "sigmab2b1": sigmab2b1,
            "chi2": chi2,
            "tau": tau,
        }

        for ip in range(3):
            context["N%d" % (ip + 1)] = N[ip]
            context["B%d" % (ip + 1)] = B[ip]
            if ip == 0:
                context["mean%d" % (ip + 1)] = mean[ip]
            else:
                context["dm_%d" % (ip + 1)] = dm[ip-1]

            context["dmb2b1_%d" % (ip + 1)] = dmb2b1[ip]
            context["frac%d" % (ip + 1)] = frac[ip]
            context["a%d" % (ip + 1)] = a[ip]
            context["n%d" % (ip + 1)] = n[ip]

            if ip > 0:
                context["sfrac%dp1p" % (ip + 1)] = sfrac[ip - 1]

        for iphi in range(5):
            context["phi%d" % (iphi + 1)] = phi[iphi]
        print renderer.render_name("fits1s", context)
print renderer.render_name("fits1s-foot", {})