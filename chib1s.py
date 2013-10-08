#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 800, 600)

from lib.chib import ChibModel
from lib import fit
from lib import db
from lib import utils

import sys
import shelve
from ext.blessings import Terminal
t = Terminal()

db = db.DB(mc="mc_1s")

def _sfracs(bin):
    db = shelve.open("data/mc_1s.db", "r")
    tbin = tuple(bin)

    if tbin in db["fits"]:
        db_fits = db["fits"][tuple(tbin)]
        s1 = db_fits["cb11"]["sigma"][0]
        # s2s1 = db_fits["cb12"]["sigma"][0] / s1
        # s3s1 = db_fits["cb13"]["sigma"][0] / s1
        # return s1, s2s1, s3s1
        return s1, 1.5 if bin != (22, 30) else 1.6, 2
    return None

def _lambda(pt_ups1):
    # default_frac = 0.5

    # a1 = db.alphab1(bin, 1)
    # a2 = db.alphab1(bin, 2)
    # a3 = db.alphab1(bin, 3)
    # if not (a1 or a2 or a3):
    #     print t.red("No b1 fraction informaition for the bin")
    # frac = (a1 if a1 else 0.6, a2 if a2 else 0.5, a3 if a3 else 0.5)
    # frac = (0.6, 0.5, 0.5)

    a1 = 0.5 if pt_ups1 < 10 else 0.6
    if pt_ups1 < 8:
        a2 = a3 = 0.4
    elif pt_ups1 < 22:
        a2 = a3 = 0.5
    else:
        a2 = a3 = 0.6

    result = [a1, a2, a3]
    return result

cfg = utils.json("configs/chib1s.json")
name = cfg["name"]

year = sys.argv[1]
pt_ups1 = int(sys.argv[2])
pt_ups2 = int(sys.argv[3]) if sys.argv[3] != '0' else None

cut = cfg["cut"]
bin = (pt_ups1, pt_ups2)
cut["pt_ups"] = bin

cut["dmplusm1s"] = [cfg["binning_default"][0], cfg["binning_default"][1]]
nbins = cfg["binning_default"][2]

if pt_ups1 < 8:
    order = 5
elif pt_ups1 < 12:
    order = 4
else:
    order = 2
# order=2
print t.yellow("Polynom order: "), order

if "lambda" not in cfg:
    frac = _lambda(pt_ups1)
else:
    l = cfg["lambda"]
    frac = [l]*3

print t.yellow("current b1 fractions: "), str(frac)

sfracs = _sfracs(bin)
if sfracs:
    print t.yellow("MC sigma[chi_b1(1P)]: "), sfracs[0]
    print t.yellow("MC sigma[chi_b1(2P)]/sigma[chi_b1(1P)]: "), sfracs[1]
    print t.yellow("MC sigma[chi_b1(3P)]/sigma[chi_b1(1P)]: "), sfracs[2]
else:
    print t.red("No MC sigma informaition for the bin")

if "fixed_mean_3p" in cfg:
    mean_3p = cfg["fixed_mean_3p"]
else:
    mean_3p = pdg.CHIB13P

print t.yellow("Mass of chib(3P): "), mean_3p


has_3p = True if pt_ups1 >= 12 else False
if year == "2011" and pt_ups1 == 12 and pt_ups2 == 14:
    has_3p = False
print t.yellow("Has chib(3P): "), has_3p

tuples = ROOT.TChain("ChibAlg/Chib")
if year == 'all':
    tuples.Add(cfg["tuples2011"])
    tuples.Add(cfg["tuples2012"])
else:
    tuples.Add(cfg["tuples%s" % year])

canvas.SetTitle("%d-%s %s" % (pt_ups1, pt_ups2, year))

# Width from database

model = ChibModel(canvas=canvas,
                  dm_begin=cut["dmplusm1s"][0],
                  dm_end=cut["dmplusm1s"][1],
                  nbins=nbins,
                  bgorder=order,
                  frac=frac,
                  sfracs=sfracs,
                  mean_3p=mean_3p,
                  has_3p=has_3p)


if "fixed_mean" in cfg:
    model.chib1p.mean1.fix(cfg["fixed_mean"])


f = fit.Fit(model=model,
            tuples=tuples,
            cut=cut,
            field="dmplusm1s",
            is_unbinned=cfg["is_unbinned"],
            nbins=nbins,
            has_splot=cfg["has_splot"])
f.year = str(year)
status = f.process()

print f
if status:
    utils.savefit(f, canvas, name)
else:
    t.red("Bad fit")
