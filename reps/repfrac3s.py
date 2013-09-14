#!/usr/bin/env ipython

""" Summary table for fraction determination """
# ============================================================================
# ============================================================================
BINNING = [(27, 40)]
# ============================================================================
import ROOT
from AnalysisPython.PyRoUts import VE

from lib import utils
from lib import pdg
from lib import db
from lib import graph

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
db = db.DB(chib="chib3s", mc="mc_3s", iups=3)
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================
for year in ["2011", "2012"]:
    chib = [""]
    u3s = ""
    eff = [""]
    frac = [""]

    for bin in BINNING:
        nups = db.nups(year, bin, ns=3)
        u3s += " & %s" % utils.latex_ve(nups)
        for ip in range(1):
            chib[ip] += " & "
            eff[ip] += " & "
            frac[ip] += " & "

            nchib = db.nchib(year=year, bin=bin, np=ip + 3)
            neff = db.eff(bin=bin, np=ip + 3, ns=3)
            nfrac = db.frac(year=year, bin=bin, np=ip + 3, ns=3)

            chib[ip] += " %s" % utils.latex_ve(nchib)
            eff[ip] += " %s" % utils.latex_ve(neff * 100)
            frac[ip] += " %s" % utils.latex_ve(nfrac * 100)

    context = {
        "alignment": "c" * (len(BINNING)),
        "nbins": len(BINNING),
        "bins": bins
    }
    for ip in range(1):
        context["chib%d" % (ip + 3)] = chib[ip]
        context["e%d" % (ip + 3)] = eff[ip]
        context["f%d" % (ip + 3)] = frac[ip]
    context["u3s"] = u3s
    print renderer.render_name("frac3s", context)
# ============================================================================
colors = {"2011": ROOT.kBlue, "2012": ROOT.kRed}
markers = {"2011": ROOT.kFullSquare, "2012": ROOT.kOpenCircle}


for ip in range(1):
    graphs = []

    for year in ["2011", "2012"]:
        values = []
        for bin in BINNING:
            nchib = db.nchib(year, bin, ip + 3)
            nfrac = db.frac(year=year, bin=bin, np=ip + 3, ns=3)
            values.append((bin, nfrac*100))
        g = graph.Graph(color=colors[
                        year], marker=markers[year], values=values)
        graphs.append(g)

    mg = graph.MultiGraph(graphs=graphs)
    mg.draw()
    mg.canvas.SaveAs("figs/frac/cb%d_frac_3s.pdf" % (ip+3))
