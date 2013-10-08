#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 800, 600)

from lib.chib2s import ChibModel
from lib import fit
from lib import db
from lib import utils

import sys
import shelve
from IPython import embed as shell
from ext.blessings import Terminal
t = Terminal()

db = db.DB()

def _sfracs(bin):
    db = shelve.open("data/mc_2s_prob.db", "r")
    tbin = tuple(bin)
    if tbin in db["fits"]:
        db_fits = db["fits"][tuple(tbin)]
        s2 = db_fits["cb12"]["sigma"][0]
        s3s2 = db_fits["cb13"]["sigma"][0] / s2
        return s2, s3s2
    print t.red("No sigma information from MC")
    return None

cfg = utils.json("configs/chib2s.json")
name = cfg["name"]

year = int(sys.argv[1])
pt_ups1 = int(sys.argv[2])
pt_ups2 = int(sys.argv[3]) if sys.argv[3] != '0' else None

cut = cfg["cut"]
bin = (pt_ups1, pt_ups2)
cut["pt_ups"] = bin

cut["dmplusm2s"] = [cfg["binning_default"][0], cfg["binning_default"][1]]
nbins = cfg["binning_default"][2]

default_frac = 0.5

a1 = db.alphab1(bin, 1)
a2 = db.alphab1(bin, 2)
a3 = db.alphab1(bin, 3)

if "lambda" not in cfg:
  if not (a1 or a2 or a3):
    print t.red("No b1 fraction informaition for the bin")
  frac = (a1 if a1 else 0.6, a2 if a2 else 0.5, a3 if a3 else 0.5)
else:
    l = cfg["lambda"]
    frac = [l]*3

print t.yellow("current b1 fractions: "), str(frac)

sfracs = _sfracs(bin)
if not sfracs:
  sfracs = (0.011, 1.77)
print t.yellow("Sigmas sigma2, sigma3/sigma2:"), sfracs

if "fixed_mean_3p" in cfg:
    mean_3p = cfg["fixed_mean_3p"]
else:
    mean_3p = pdg.CHIB13P

print t.yellow("chib1(3P) mass:"), mean_3p

tuples_file = cfg["tuples%d" % year]
tuples = ROOT.TChain("ChibAlg/Chib")
tuples.Add(tuples_file)

canvas.SetTitle("%d-%s %d" % (pt_ups1, pt_ups2, year))


# # Width from database
# mc_width = []
model = ChibModel(canvas=canvas,
                  dm_begin=cut["dmplusm2s"][0],
                  dm_end=cut["dmplusm2s"][1],
                  nbins=nbins,
                  bgorder=3,
                  frac=frac,
                  sfracs=sfracs,
                  has_3p=True)

if "fixed_mean" in cfg:
    model.chib2p.mean1.fix(cfg["fixed_mean"])
    model.chib3p.dm2p.fix(mean_3p - cfg["fixed_mean"])

f = fit.Fit(model=model,
            tuples=tuples,
            cut=cut,
            field="dmplusm2s",
            is_unbinned=cfg["is_unbinned"],
            nbins=nbins,
            has_splot=cfg["has_splot"])
f.year = str(year)
status = f.process()
print f

if status:
    utils.savefit(f, canvas, name)
else:
    print t.red("Bad fit")

