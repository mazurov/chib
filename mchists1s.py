#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 1024, 768)

import AnalysisPython.PyRoUts as RU
from AnalysisPython.PyRoUts import VE
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
print t.yellow("Basic chib cut:"), basic_cut

db = shelve.open("data/mc_elist.db")


mc_elist = db.get("elist", None)
if not mc_elist:
    tuples.Draw(">>mc_elist", basic_cut, "entrylist")
    mc_elist = ROOT.gROOT.FindObject("mc_elist")
    db["elist"] = mc_elist
tuples.SetEntryList(mc_elist)

for np in range(3):
    h1 = ROOT.TH1D("h1", "h1", 200, 0, 2)
    h1.SetLineWidth(2)
    h1.SetLineColor(ROOT.kRed)
    tuples.Draw("dm >> h1", "np==%d && nb==1" % (np+1))

    h2 = ROOT.TH1D("h2", "h2", 200, 0, 2)
    h2.SetLineWidth(2)
    h2.SetLineColor(ROOT.kBlue)
    h2.SetLineStyle(ROOT.kDotted)
    tuples.Draw("dm >> h2", "np==%d && nb==2" % (np+1), "same")

    canvas.SaveAs("figs/mc/hists/cb%d_h.pdf" % (np+1))

for np in range(1):
    hists = []
    # h1 = RU.h1_axis(axis, "","h1")
    h1 = ROOT.TH1D("h1", "h1", 24, 6, 30)
    # h1.Sumw2()
    h1.SetLineWidth(2)
    h1.SetLineColor(ROOT.kRed)
    n1 = tuples.Draw("pt_chib >> h1", "np==%d && nb==1" % (np+1))
    # h1.Scale(1.0/h1.Integral())
    hists.append(h1)

    # h2 = RU.h1_axis(axis, "","h2")
    h2 = ROOT.TH1D("h2", "h2", 24, 6, 30)
    # h2.Sumw2()
    h2.SetLineWidth(2)
    h2.SetLineColor(ROOT.kBlue)
    h2.SetLineStyle(ROOT.kDotted)
    n2 = tuples.Draw("pt_chib >> h2", "np==%d && nb==2" % (np+1))
    # h2.Scale(1.0/h2.Integral())
    hists.append(h2)


    hists = sorted(hists, key=lambda h: -h.GetMaximum())
    same = ""
    for h in hists:
        h.Draw(same)
        same = "same"

    print "b1=", n1, " b2=", n2
    canvas.SaveAs("figs/mc/hists/cb%d_h_pt_chib.pdf" % (np+1))
    br = VE(0.2, 0.04**2)/VE(0.35, 0.08**2)
    h3 = h2/h1
    h3.SetLineColor(ROOT.kBlack)
    h3.SetLineStyle(ROOT.kSolid)
    h3.SetMarkerStyle(ROOT.kOpenCircle)
    h3.Draw("A")
    canvas.SaveAs("figs/mc/hists/cb%d_b2_b1_frac.pdf" % (np+1))



# utuples = ROOT.TChain("UpsilonAlg/Upsilon")
# utuples.Add(cfg["tuples"])

# basic_cut = utils.cut_expr(cfg["ucut"])
# print t.yellow("Basic upsilon cut:"), basic_cut

# mc_ulist = db.get("ulist", None)
# if not mc_ulist:
#     utuples.Draw(">>mc_ulist", basic_cut, "entrylist")
#     mc_ulist = ROOT.gROOT.FindObject("mc_ulist")
#     db["ulist"] = mc_ulist
# utuples.SetEntryList(mc_ulist)

# axis = [6, 8, 10, 12, 14, 18, 22, 30]
# for np in range(1):
#     hists = []
#     # h1 = RU.h1_axis(axis, "","h1")
#     h1 = ROOT.TH1D("h1", "h1", 30, 0, 30)
#     h1.Sumw2()
#     h1.SetLineWidth(2)
#     h1.SetLineColor(ROOT.kRed)
#     n1 = utuples.Draw("pt_ups >> h1", "np==%d && nb==1" % (np+1))
#     # h1.Scale(1.0/h1.Integral())
#     hists.append(h1)

#     # h2 = RU.h1_axis(axis, "","h2")
#     h2 = ROOT.TH1D("h2", "h2", 30, 0, 30)
#     h2.Sumw2()
#     h2.SetLineWidth(2)
#     h2.SetLineColor(ROOT.kBlue)
#     h2.SetLineStyle(ROOT.kDotted)
#     n2 = utuples.Draw("pt_ups >> h2", "np==%d && nb==2" % (np+1))
#     # h2.Scale(1.0/h2.Integral())
#     hists.append(h2)


#     hists = sorted(hists, key=lambda h: -h.GetMaximum())
#     same = ""
#     for h in hists:
#         h.Draw(same)
#         same = "same"

#     print "b1=", n1, " b2=", n2
#     canvas.SaveAs("figs/mc/hists/cb%d_h_pt_ups.pdf" % (np+1))
#     br = VE(0.2, 0.04**2)/VE(0.35, 0.08**2)
#     h3 = h2/h1
#     h3.SetLineColor(ROOT.kBlack)
#     h3.SetLineStyle(ROOT.kSolid)
#     h3.SetMarkerStyle(ROOT.kOpenCircle)
#     # h3 = h1/h2
#     h3.Draw()
#     canvas.SaveAs("figs/mc/hists/cb%d_b2_b1_ufrac.pdf" % (np+1))

# db.close()