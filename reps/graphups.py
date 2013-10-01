#!/usr/bin/env ipython

from lib.db import DBUps
from lib import graph

db = DBUps()


BINNING = [(0, 6), (6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)]

for ip in range(3):
    ns = ip + 1
    graphs = []

    for year in ["2011", "2012"]:
        values = []
        for bin in BINNING:
            nups = db.nups(year, bin, ns)
            values.append((bin, nups/(bin[1] - bin[0]) if nups else None))

        g = graph.Graph(color=graph.COLORS[year],
                        marker=graph.MARKERS[year],
                        values=values, space=10)
        graphs.append(g)

    mg = graph.MultiGraph(graphs=graphs, ymin=0)
    mg.draw()
    mg.canvas.SaveAs("figs/graphups/nups%ds.pdf" % ns)


graphs = []
for year in ["2011", "2012"]:
    values = []
    for bin in BINNING:
        m = db.mass(year, bin)
        values.append((bin, m))

    g = graph.Graph(color=graph.COLORS[year],
                    marker=graph.MARKERS[year],
                    values=values, space=3)
    graphs.append(g)

mg = graph.MultiGraph(graphs=graphs)
mg.draw()
mg.canvas.SaveAs("figs/graphups/mups1s.pdf")

