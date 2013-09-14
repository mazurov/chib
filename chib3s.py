#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 800, 600)

from lib.chib3s import ChibModel
from lib import fit
from lib import db
from lib import utils

import sys
import shelve
from IPython import embed as shell
from ext.blessings import Terminal
t = Terminal()

db = db.DB()


def save(fit):
    bin = tuple(fit.cut["pt_ups"])
    db = shelve.open('data/chib3s.db')
    year = db.get(fit.year, {})
    year[bin] = fit.model.params()
    db[fit.year] = year
    db.close()
    canvas.SaveAs("figs/data/fits3s/f%s_%d_%s.pdf" %
                  (fit.year, bin[0], str(bin[1])))


def _sfracs(bin):
    db = shelve.open("data/mc_3s.db", "r")
    tbin = tuple(bin)
    if tbin in db["fits"]:
        db_fits = db["fits"][tuple(tbin)]
        s3 = db_fits["cb13"]["sigma"][0]
        return s3
    return None

cfg = utils.json("configs/chib3s.json")

year = sys.argv[1]
pt_ups1 = int(sys.argv[2])
pt_ups2 = int(sys.argv[3]) if sys.argv[3] != '0' else None

cut = cfg["cut"]
bin = (pt_ups1, pt_ups2)
cut["pt_ups"] = bin

cut["dm"] = [cfg["binning_default"][0], cfg["binning_default"][1]]
nbins = cfg["binning_default"][2]

default_frac = 0.5

a1 = db.alphab1(bin, 1)
a2 = db.alphab1(bin, 2)
a3 = db.alphab1(bin, 3)

if not (a1 or a2 or a3):
    print t.red("No b1 fraction informaition for the bin")
frac = (a1 if a1 else 0.6, a2 if a2 else 0.5, a3 if a3 else 0.5)
# frac = (0.6, 0.5, 0.5)
print t.yellow("current b1 fractions: "), str(frac)

sigma = _sfracs(bin)
# print t.yellow("Sigmas sigma2, sigma3/sigma2:"), sfracs

tuples = ROOT.TChain("ChibAlg/Chib")
if year == 'all':
    tuples.Add(cfg["tuples2011"])
    tuples.Add(cfg["tuples2012"])
else:
    tuples.Add(cfg["tuples%s" % year])


canvas.SetTitle("%d-%s %s" % (pt_ups1, pt_ups2, year))


# Width from database
# mc_width = []
model = ChibModel(canvas=canvas,
                  dm_begin=cut["dm"][0],
                  dm_end=cut["dm"][1],
                  nbins=nbins,
                  bgorder=2,
                  frac=frac,
                  sigma=None,
                  has_3p=True)
# model.chib3p.frac.setConstant(False)

f = fit.Fit(model=model,
            tuples=tuples,
            cut=cut,
            field="dm",
            is_unbinned=cfg["is_unbinned"],
            nbins=nbins,
            has_splot=cfg["has_splot"])
f.year = year
f.process()
print f
