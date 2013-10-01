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


def save(fit, suffix="dtf"):
    bin = tuple(fit.cut["pt_ups"])
    db = shelve.open('data/ups_%s.db' % suffix)
    year = db.get(fit.year, {})
    year[bin] = fit.model.params()
    db[fit.year] = year
    print(db[fit.year])
    db.close()

    figname = fit.year + ("_" + suffix if suffix else "")
    canvas.SaveAs("figs/data/ufits/f%s_%d_%s.pdf" %
                  (figname, bin[0], str(bin[1])))


cfg = utils.json("configs/ups.json")

year = int(sys.argv[1])
pt_ups1 = int(sys.argv[2])
pt_ups2 = int(sys.argv[3]) if sys.argv[3] != '0' else None

cut = cfg["cut"]
cut["pt_ups"] = [pt_ups1, pt_ups2]
cut["m_dtf"] = [cfg["binning_default"][0], cfg["binning_default"][1]]
nbins = cfg["binning_default"][2]


tuples_file = cfg["tuples%d" % year]
tuples = ROOT.TChain("UpsilonAlg/Upsilon")
tuples.Add(tuples_file)

canvas.SetTitle("%d-%s %d" % (pt_ups1, pt_ups2, year))

# Width from database
model = UpsModel(canvas=canvas,
                 m1=cut["m_dtf"][0],
                 m2=cut["m_dtf"][1],
                 nbins=nbins,
                 is_pull=cfg["is_pull"]
                 )

if "fixed_mean" in cfg:
    model.m1s.fix(cfg["fixed_mean"])

# model.chib1p.sigma.fix(0.022)
f = fit.Fit(model=model,
            tuples=tuples,
            cut=cut,
            field="m_dtf",
            is_unbinned=cfg["is_unbinned"],
            nbins=nbins)
f.year = str(year)
f.process()
print f
save(f)
