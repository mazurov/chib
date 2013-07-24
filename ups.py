#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 800, 600)

from lib.ups import UpsModel
from lib import fit
from lib import utils

import sys
import shelve
from ext.blessings import Terminal
t = Terminal()


def save(fit):
    bin = tuple(fit.cut["pt_ups"])
    db = shelve.open('data/ups.db')
    year = db.get(fit.year, {})
    year[bin] = fit.model.params()
    db[fit.year] = year
    db.close()


cfg = utils.json("configs/ups.json")

year = int(sys.argv[1])
pt_ups1 = int(sys.argv[2])
pt_ups2 = int(sys.argv[3]) if sys.argv[3] != '0' else None

cut = cfg["cut"]
cut["pt_ups"] = [pt_ups1, pt_ups2]
cut["m"] = [cfg["binning_default"][0], cfg["binning_default"][1]]
nbins = cfg["binning_default"][2]


tuples_file = cfg["tuples%d" % year]
tuples = ROOT.TChain("UpsilonAlg/Upsilon")
tuples.Add(tuples_file)

canvas.SetTitle("%d-%s %d" % (pt_ups1, pt_ups2, year))

# Width from database
model = UpsModel(canvas=canvas,
                 m1=cut["m"][0],
                 m2=cut["m"][1],
                 nbins=nbins,
                 )
# model.chib1p.sigma.fix(0.022)
f = fit.Fit(model=model,
            tuples=tuples,
            cut=cut,
            field="m",
            is_unbinned=cfg["is_unbinned"],
            nbins=nbins)
f.year = str(year)
f.process()
print f
