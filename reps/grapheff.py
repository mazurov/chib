#!/usr/bin/env ipython

from lib.db import DBMC
from lib import graph


BINNINGS = {
    1: [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)],
    2: [(18, 25), (25, 40)]
}

for ns in range(1, 3):
    db = DBMC("mc_%ds_tr" % ns)
    binning = BINNINGS[ns]
    graphs = []
    for np in range(ns, 4):
        values = []
        for bin in binning:
            val = db.eff(bin, np=np, ns=ns)
            values.append((bin, val*100))

        g = graph.Graph(color=graph.CHIB_COLORS[np],
                        marker=graph.CHIB_MARKERS[np],
                        values=values)
        graphs.append(g)

    mg = graph.MultiGraph(graphs=graphs, ymin=0)
    mg.draw()
    mg.canvas.SaveAs("figs/mc/eff/cb_ups%ds.pdf" % ns)
