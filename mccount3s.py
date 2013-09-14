#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 1024, 768)

from lib import utils

import sys
import shelve
from IPython import embed as shell  # noqa
from ext.blessings import Terminal
from collections import defaultdict


def save(result):
    db = shelve.open('data/mc_3s.db')
    count = db.get("u3s", {})

    count.update(dict(result))

    db["u3s"] = count
    db.close()

t = Terminal()
cfg = utils.json("configs/mcfits3s.json")

tuples = ROOT.TChain("UpsilonAlg/Upsilon")
tuples.Add(cfg["tuples"])

basic_cut = utils.cut_expr(cfg["ucut"])
print t.yellow("Basic cut:"), basic_cut

db = shelve.open("data/mc_elist3s.db")
mc_ulist = db.get("ulist", None)

# if not mc_ulist:
if True:
    tuples.Draw(">>mc_ulist", basic_cut, "entrylist")
    mc_ulist = ROOT.gROOT.FindObject("mc_ulist")
    db["ulist"] = mc_ulist
db.close()

tuples.SetEntryList(mc_ulist)


binning = [(27, 40)]

result = defaultdict(dict)
np = 3
for nb in range(2):
    cut = {"np": np, "nb": nb + 1}
    db_key = "cb%d%d" % (nb + 1, np)
    for bin in binning:
        cut["pt_ups"] = bin
        cut_expr = utils.cut_expr(cut)
        print t.yellow("Cut:"), cut_expr
        n = tuples.Draw("m", cut_expr)
        result[bin][db_key] = n

print t.green(str(result))
