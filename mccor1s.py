#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 800, 600)
canvas.SetGridx(True)
canvas.SetGridy(True)

from lib import utils

from IPython import embed as shell  # noqa
from ext.blessings import Terminal
t = Terminal()

import sys
import shelve
cfg = utils.json("configs/mcfits1s.json")

tuples = ROOT.TChain("ChibAlg/Chib")
tuples.Add(cfg["tuples"])

basic_cut = utils.cut_expr(cfg["cut"])
print t.yellow("Basic cut:"), basic_cut

db = shelve.open("data/mc_elist.db")
mc_elist = db.get("elist", None)
# if True:
if not mc_elist:
    tuples.Draw(">>mc_elist", basic_cut, "entrylist")
    mc_elist = ROOT.gROOT.FindObject("mc_elist")
    db["elist"] = mc_elist
db.close()

tuples.SetEntryList(mc_elist)
ranges = [(0.38, 0.48), (0.7, 0.9), (0.95, 1.15)]
hists = [
    [(0.5, 1.2), (0.5, 1.05),  (0.1, 2.5)],
    [(0.1, 2.2), (0.5, 2), (0.1, 3)],
    [(0.1, 3), (0.5, 2.6),  (0.5, 3.5)]
]
for np in range(3):
    for nb in range(1):
        name = "chib{b}({p}P)".format(b=nb+1, p=np+1)
        cut = {"np": np+1, "nb": nb+1}
        for tail in range(3):
            cut["pt_ups"] = (8, 10)
            if tail == 0:  # left
                tail_name = "left"
                cut["dm"] = [None, ranges[np][0]]
            elif tail == 1:  # peak
                tail_name = "peak"
                cut["dm"] = [ranges[np][0], ranges[np][1]]
                cut["pt_ups"] = (8, 8.1)
            else:
                tail_name = "right"
                cut["dm"] = [ranges[np][1], None]

            cut_expr = utils.cut_expr(cut)
            print t.yellow("Cut expression for %s:" % name), cut_expr
            axis = hists[np][tail]
            hh = ROOT.TH2F("hh","hh", 60, axis[0], axis[1], 60, axis[0],
                           axis[1])
            hh.GetXaxis().SetNdivisions(505)
            hh.GetYaxis().SetNdivisions(505)

            tuples.Draw("pt_g:mc_cb_g_pt/1000 >> hh", cut_expr)

            image_name = "figs/cb%d%d_cor_%s.pdf" % (nb+1, np+1, tail_name)
            canvas.SaveAs(image_name)
