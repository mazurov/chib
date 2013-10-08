#!/usr/bin/env ipython

""" Summary table for fraction determination """
# ============================================================================
# ============================================================================
BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30),
           (18, 30)]
EXCLUDE23P = [(18, 22), (22, 30)]
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
db = db.DB(chib="chib1s_tr", mc="mc_1s_tr", iups=1)
# ============================================================================
alignment = "c" * (len(BINNING))
# ============================================================================
bins = ""
for bin in BINNING:
    bins += " & %d --- %d" % bin
# ============================================================================
for year in ["2011", "2012"]:
    chib = ["", "", ""]
    u1s = ""
    eff = ["", "", ""]
    frac = ["", "", ""]

    for bin in BINNING:
        nups = db.nups(year, bin, 1)
        u1s += " & %s" % utils.latex_ve(nups)
        for ip in range(3):
            chib[ip] += " & "
            eff[ip] += " & "
            frac[ip] += " & "

            nchib = db.nchib(year, bin, ip + 1)

            if ((ip > 1 and (bin in EXCLUDE23P)) or (not nchib) or
                    (nchib.value() == 0)):
                    chib[ip] += " --- "
                    eff[ip] += " --- "
                    frac[ip] += " --- "
                    continue

            neff = db.eff(bin, ip + 1)
            nfrac = db.frac(year, bin, ip + 1, 1)

            chib[ip] += " %s" % utils.latex_ve(nchib)
            eff[ip] += " %s" % utils.latex_ve(neff * 100)
            frac[ip] += " %s" % utils.latex_ve(nfrac * 100)

    context = {
        "alignment": "c" * (len(BINNING)),
        "nbins": len(BINNING),
        "bins": bins
    }
    for ip in range(3):
        context["chib%d" % (ip + 1)] = chib[ip]
        context["e%d" % (ip + 1)] = eff[ip]
        context["f%d" % (ip + 1)] = frac[ip]
    context["u1s"] = u1s
    print renderer.render_name("frac1s", context)
# ============================================================================
colors = {"2011": ROOT.kBlue, "2012": ROOT.kRed}
markers = {"2011": ROOT.kFullSquare, "2012": ROOT.kOpenCircle}


for ip in range(3):
    graphs = []
    if ip == 0:
        binning = BINNING[:-1]
    else:
        binning = BINNING[:-3] + [(18, 30)]

    for year in ["2011", "2012"]:
        values = []
        for bin in binning:
            nchib = db.nchib(year, bin, ip + 1)
            if ((ip > 1 and (bin in EXCLUDE23P)) or (not nchib) or
               (nchib.value() == 0)):
                values.append((bin, None))
            else:
                nfrac = db.frac(year, bin, ip + 1, 1)
                values.append((bin, nfrac*100))
        g = graph.Graph(color=colors[
                        year], marker=markers[year],
                        values=values,
                        space=2)
        graphs.append(g)

    mg = graph.MultiGraph(graphs=graphs, ymin=0)
    mg.draw()
    mg.canvas.SaveAs("figs/frac/cb%d_frac.pdf" % (ip+1))
