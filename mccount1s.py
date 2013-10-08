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
    db = shelve.open('data/mc_1s_tr.db')
    count = db.get("u1s", {})

    count.update(dict(result))

    db["u1s"] = count
    db.close()

t = Terminal()
cfg = utils.json("configs/mcfits1s.json")

tuples = ROOT.TChain("UpsilonAlg/Upsilon")
tuples.Add(cfg["tuples"])

basic_cut = utils.cut_expr(cfg["ucut"])
print t.yellow("Basic cut:"), basic_cut

db = shelve.open("data/mc_elist.db")
mc_ulist = db.get("ulist", None)

# if not mc_ulist:
if True:
    tuples.Draw(">>mc_ulist", basic_cut, "entrylist")
    mc_ulist = ROOT.gROOT.FindObject("mc_ulist")
    db["ulist"] = mc_ulist
db.close()

tuples.SetEntryList(mc_ulist)


binning = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 30), (18, 22),
           (22, 30)]

result = defaultdict(dict)
for np in range(3):
    for nb in range(2):
        cut = {"np": np + 1, "nb": nb + 1}
        db_key = "cb%d%d" % (nb + 1, np + 1)
        for bin in binning:
            cut["pt_ups"] = bin
            cut_expr = utils.cut_expr(cut)
            print t.yellow("Cut:"), cut_expr
            n = tuples.Draw("m", cut_expr)
            result[bin][db_key] = n

print t.green(str(result))
