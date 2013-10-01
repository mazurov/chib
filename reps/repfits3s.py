#!/usr/bin/env ipython

""" Print MC fit parameters """
# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
# BINNING = [(18, 22), (22, 40)]
BINNING = [(27, None)]
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
db = db.DB(chib="chib3s_fix", mc="mc_3s_prob", iups=2)
# ============================================================================
alignment = "rrr" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & & \multicolumn{2}{c}{%s}" % (
            "$%s < p_T(\Y3S) < %s \gevc$" % bin if bin[1] else "$p_T(\Y3S)> %d \gevc$" % bin[0]
    )
years = ""
lines = ""

i = 3
for bin in BINNING:
    years += " && \sqs = 7 \\tev & \sqs = 8\\tev"
    lines += "\cmidrule{%d-%d}" % (i, i + 1)
    i += 3


N = ""
B = ""
mean = ""
dm = ""
dmb2b1 = ""
frac = ""
a = ""
n = ""
sigma = ""

tau = ""
phi = ["", "", "", "", ""]

chi2 = ""
for bin in BINNING:
    # Float parameters
    # N, mean, background, x2
    for year in ["2011", "2012"]:
        fit = db.fit(year, bin)

        key = "mean_b1_3p"
        mean += tmpl.output(year, fit, key, scale=1000)

        key = "N3P"
        N += tmpl.output(year, fit, key)

        key = "dmb2b1_3p"
        dmb2b1 += tmpl.output(year, fit, key, scale=1000, digits=2)

        key = "frac3"
        frac += tmpl.output(year, fit, key, digits=1)

        key = "a3"
        a += tmpl.output(year, fit, key, digits=2)

        key = "n3"
        n += tmpl.output(year, fit, key, digits=1)

        B += tmpl.output(year, fit, "B")

        sigma += tmpl.output(year, fit, "sigma_b1_3p", scale=1000)

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
        "mean3": mean,
        "sigma": sigma,
        "chi2": chi2,
        "tau": tau,
    }

    context["N3"] = N
    context["B3"] = B

    context["dmb2b1_3"] = dmb2b1
    context["frac3"] = frac
    context["a3"] = a
    context["n3"] = n

    context["dm_3"] = dm

    for iphi in range(5):
        context["phi%d" % iphi] = phi[iphi]

print renderer.render_name("fits3s", context)
