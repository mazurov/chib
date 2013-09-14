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

utuples = ROOT.TChain("UpsilonAlg/Upsilon")
utuples.Add(cfg["tuples"])

basic_cut = utils.cut_expr(cfg["ucut"])
print t.yellow("Basic upsilon cut:"), basic_cut

mc_ulist = db.get("ulist", None)
if not mc_ulist:
    utuples.Draw(">>mc_ulist", basic_cut, "entrylist")
    mc_ulist = ROOT.gROOT.FindObject("mc_ulist")
    db["ulist"] = mc_ulist
utuples.SetEntryList(mc_ulist)

