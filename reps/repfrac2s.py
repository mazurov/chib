#!/usr/bin/env ipython

""" Summary table for fraction determination """
# ============================================================================
# ============================================================================
BINNING = [(18, 22), (22, 30)]
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
db = db.DB(chib="chib2s", mc="mc_2s", iups=2)
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================
for year in ["2011", "2012"]:
    chib = ["", ""]
    u2s = ""
    eff = ["", ""]
    frac = ["", ""]

    for bin in BINNING:
        nups = db.nups(year, bin, ns=2)
        u2s += " & %s" % utils.latex_ve(nups)
        for ip in range(2):
            chib[ip] += " & "
            eff[ip] += " & "
            frac[ip] += " & "

            nchib = db.nchib(year=year, bin=bin, np=ip + 2)
            neff = db.eff(bin=bin, np=ip + 2, ns=2)
            nfrac = db.frac(year=year, bin=bin, np=ip + 2, ns=2)

            chib[ip] += " %s" % utils.latex_ve(nchib)
            eff[ip] += " %s" % utils.latex_ve(neff * 100)
            frac[ip] += " %s" % utils.latex_ve(nfrac * 100)

    context = {
        "alignment": "c" * (len(BINNING)),
        "nbins": len(BINNING),
        "bins": bins
    }
    for ip in range(2):
        context["chib%d" % (ip + 2)] = chib[ip]
        context["e%d" % (ip + 2)] = eff[ip]
        context["f%d" % (ip + 2)] = frac[ip]
    context["u2s"] = u2s
    print renderer.render_name("frac2s", context)
# ============================================================================
colors = {"2011": ROOT.kBlue, "2012": ROOT.kRed}
markers = {"2011": ROOT.kFullSquare, "2012": ROOT.kOpenCircle}


for ip in range(2):
    graphs = []

    for year in ["2011", "2012"]:
        values = []
        for bin in BINNING:
            nchib = db.nchib(year, bin, ip + 2)
            nfrac = db.frac(year, bin, ip + 2, 2)
            values.append((bin, nfrac*100))
        g = graph.Graph(color=colors[
                        year], marker=markers[year], values=values)
        graphs.append(g)

    mg = graph.MultiGraph(graphs=graphs)
    mg.draw()
    mg.canvas.SaveAs("figs/frac/cb%d_frac_2s.pdf" % (ip+2))
