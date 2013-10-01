#!/usr/bin/env ipython

from lib.db import DBChib
from lib import graph

NS = 2
db = DBChib(path="chib%ds_mfix" % NS)


for ip in range(2):
    np = ip + 2
    graphs = []

    # BINNING = [(0, 6), (6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)]
    BINNING = [(18, 25), (25, 40)]

    for year in ["2011", "2012"]:
        values = []
        for bin in BINNING:
            # v = db.mass(year, bin, np)
            v = db.nchib(year, bin, np)
            values.append((bin, v))

        g = graph.Graph(color=graph.COLORS[year],
                        marker=graph.MARKERS[year],
                        values=values)
        graphs.append(g)

    mg = graph.MultiGraph(graphs=graphs, ymin=0)
    mg.draw()
    # mg.canvas.SaveAs("figs/graphm/mass%dp.pdf" % NP)
    mg.canvas.SaveAs("figs/graphm/n%dp_%ds.pdf" % (np, NS))
