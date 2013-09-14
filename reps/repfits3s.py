#!/usr/bin/env ipython

""" Print MC fit parameters """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNING = [(27, 40)]
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
db = db.DB(chib="chib3s", mc="mc_3s", iups=4)
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================
for year in ["2011", "2012"]:
    N = ["", ""]
    B = ""
    mean = ["", ""]
    dmb2b1 = ["", ""]
    frac = ["", ""]
    a = ["", ""]
    n = ["", ""]
    sigma = ""
    sigmab2b1 = ""
    sfrac = [""]

    tau = ""
    phi = ["","","","",""]

    chi2 = ""

    for bin in BINNING:
        fit = db.fit(year, bin)
        for ip in range(1):
            key = "N%dP" % (ip + 3)
            if key in fit:
                N[ip] += " & %s" % utils.latex_ve_pair(fit[key])
            else:
                N[ip] += " & - "

            key = "mean_b1_%dp" % (ip + 3)
            if key in fit:
                mean[ip] += " & %s" % utils.latex_ve(VE(str(fit[key])) * 1000)
            else:
                mean[ip] += " & - "

            key = "dmb2b1_%dp" % (ip + 3)
            if key in fit:
                dmb2b1[ip] += " & %s" % utils.latex_ve(
                    VE(str(fit[key])) * 1000)
            else:
                dmb2b1[ip] += " & - "


            key = "frac%d" % (ip + 3)
            if key in fit:
                frac[ip] += " & %s" % utils.latex_ve(VE(str(fit[key])))
            else:
                frac[ip] += " & - "

            key = "a%d" % (ip + 3)
            if key in fit:
                a[ip] += " & %s" % utils.latex_ve(VE(str(fit[key])))
            else:
                a[ip] += " & - "

            key = "n%d" % (ip + 3)
            if key in fit:
                n[ip] += " & %s" % utils.latex_ve(VE(str(fit[key])))
            else:
                n[ip] += " & - "



        sigma += " & %s" % utils.latex_ve(VE(str(fit["sigma_b1_3p"])) * 1000)
        B += " & %s" % utils.latex_ve_pair(fit["B"])

        tau += " & %s" % utils.latex_ve_pair(fit["exp_tau"])
        for iphi in range(5):
            key = "poly_phi%d" % (iphi+1)
            if key in fit:
                phi[iphi] += " & %s" % utils.latex_ve(VE(str(fit[key])))
            else:
                phi[iphi] += " & - "
        chi2 += " & %s" % utils.latex_ve_pair(fit["chi2"])
    context = {
        "year": year,
        "e": "7" if year == "2011" else "8",
        "alignment": alignment,
        "nbins": len(BINNING),
        "bins": bins,
        "B": B,
        "sigma": sigma,
        # "sigmab2b1": sigmab2b1,
        "chi2": chi2,
        "tau": tau,
    }

    for ip in range(1):
        context["N%d" % (ip+3)] = N[ip]
        context["B%d" % (ip+3)] = B[ip]
        context["mean%d" % (ip+3)] = mean[ip]
        context["dmb2b1_%d" % (ip+3)] = dmb2b1[ip]
        context["frac%d" % (ip+3)] = frac[ip]
        context["a%d" % (ip+3)] = a[ip]
        context["n%d" % (ip+3)] = n[ip]

    for iphi in range(5):
        context["phi%d" % (iphi + 1)] = phi[iphi]
    print renderer.render_name("fit3s", context)
