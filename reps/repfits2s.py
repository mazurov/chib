#!/usr/bin/env ipython

""" Print MC fit parameters """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
# BINNING = [(18, 22), (22, 40)]
BINNING = [(18, None)]
# ============================================================================
from lib import utils
from lib import pdg
from lib import db
from lib import tmpl

import os
import sys

# ============================================================================
renderer = tmpl.renderer()
# ============================================================================
# Extract efficencies
db = db.DB(chib="chib2s_fix", mc="mc_2s_prob", iups=2)
# ============================================================================
alignment = "rrr" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & & \multicolumn{2}{c}{%s}" % (
            "$%s < p_T(\Y2S) < %s \gevc$" % bin if bin[1] else "$p_T(\Y2S)> %d \gevc$" % bin[0]
    )
years = ""
lines = ""

i = 3
for bin in BINNING:
    years += " && \sqs = 7 \\tev & \sqs = 8\\tev"
    lines += "\cmidrule{%d-%d}" % (i, i + 1)
    i += 3


N = ["", ""]
B = ""
mean = ""
dm = ""
dmb2b1 = ["", "", ""]
frac = ["", ""]
a = ["", ""]
n = ["", ""]
sigma = ""
sigmab2b1 = ""
sfrac = ""

tau = ""
phi = ["", "", "", "", ""]

chi2 = ""
for bin in BINNING:
    # Float parameters
    # N, mean, background, x2
    for year in ["2011", "2012"]:
        fit = db.fit(year, bin)

        key = "mean_b1_2p"
        mean += tmpl.output(year, fit, key, scale=1000)

        for ip in range(2):
            np = ip + 2
            key = "N%dP" % np
            N[ip] += tmpl.output(year, fit, key)

            key = "dmb2b1_%dp" % np
            dmb2b1[ip] += tmpl.output(year, fit, key, scale=1000, digits=2)

            key = "frac%d" % np
            frac[ip] += tmpl.output(year, fit, key, digits=1)

            key = "a%d" % np
            a[ip] += tmpl.output(year, fit, key, digits=2)

            key = "n%d" % np
            n[ip] += tmpl.output(year, fit, key, digits=1)

        key = "dm_b13p_b11p"
        dm += tmpl.output(year, fit, key, scale=1000, digits=0)

        key = "sfrac3p2p"
        sfrac += tmpl.output(year, fit, key)

        B += tmpl.output(year, fit, "B")

        sigma += tmpl.output(year, fit, "sigma_b1_2p", scale=1000)
        sigmab2b1 += tmpl.output(year, fit, "sdiffb2b1")

        tau += tmpl.output(year, fit, "exp_tau")

        for iphi in range(5):
            key = "poly_phi%d" % (iphi + 1)
            phi[iphi] += tmpl.output(year, fit, key)

        chi2 += tmpl.output(year, fit, "chi2", var=True)

    context = {
        "alignment": alignment,
        "cols": 3 * len(BINNING),
        "years": years,
        "lines": lines,
        "bins": bins,
        "B": B,
        "mean2": mean,
        "sigma": sigma,
        "sigmab2b1": sigmab2b1,
        "chi2": chi2,
        "tau": tau,
    }

    for ip in range(2):
        np = ip + 2
        context["N%d" % np] = N[ip]
        context["B%d" % np] = B[ip]

        context["dmb2b1_%d" % np] = dmb2b1[ip]
        context["frac%d" % np] = frac[ip]
        context["a%d" % np] = a[ip]
        context["n%d" % np] = n[ip]

    context["dm_3"] = dm
    context["sfrac3p2p"] = sfrac

    for iphi in range(5):
        context["phi%d" % iphi] = phi[iphi]

print renderer.render_name("fits2s", context)
