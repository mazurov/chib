#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 800, 600)

import shelve
from lib import graph

from AnalysisPython.PyRoUts import VE

db = shelve.open("data/chib1s_alpha.db", "r")

binning = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)]
colors = {"2011": ROOT.kBlue, "2012": ROOT.kRed}
markers = {"2011": ROOT.kFullSquare, "2012": ROOT.kFullCircle}
graphs = []
for year in ["2011", "2012"]:
    db_year = db[year]
    values = []
    for bin in binning:
        ve = VE(str(db_year[bin]["mean_b1_1p"]))*1000
        values.append((bin, ve))
    g = graph.Graph(values=values,
                        color=colors[year],
                        marker=markers[year])
    graphs.append(g)

mg = graph.MultiGraph(graphs=graphs)
mg.draw()
