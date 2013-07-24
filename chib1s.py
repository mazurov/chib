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

db = db.DB()

def user_labels(pt_ups1, pt_ups2):
    def _user_labels(self):
        if pt_ups2 is not None:
            txt = "%d < p_{T}^{#Upsilon(1S)} < %d GeV/c" % (pt_ups1, pt_ups2)
        else:
            txt = "p_{T}^{#Upsilon(1S)} > %d GeV/c" % pt_ups1
        self.user_label = ROOT.TLatex(0.62, 0.75, txt)
        self.user_label.SetNDC()
        self.user_label.Draw()
    return _user_labels


def save(fit):
    bin = tuple(fit.cut["pt_ups"])
    db = shelve.open('data/chib1s_massg.db')
    year = db.get(fit.year, {})
    year[bin] = fit.model.params()
    db[fit.year] = year
    db.close()
    canvas.SaveAs("figs/data/fits/f%s_%d_%s.pdf" %
                  (fit.year, bin[0], str(bin[1])))


def _sfracs(bin):
    db = shelve.open("data/mc.db", "r")
    tbin = tuple(bin)
    if tbin in db["fits"]:
        db_fits = db["fits"][tuple(tbin)]
        s1 = db_fits["cb11"]["sigma"][0]
        s2s1 = db_fits["cb12"]["sigma"][0] / s1
        s3s1 = db_fits["cb13"]["sigma"][0] / s1
        return s1, s2s1, s3s1
    return None


cfg = utils.json("configs/chib1s.json")

year = int(sys.argv[1])
pt_ups1 = int(sys.argv[2])
pt_ups2 = int(sys.argv[3]) if sys.argv[3] != '0' else None

cut = cfg["cut"]
bin = (pt_ups1, pt_ups2)
cut["pt_ups"] = bin

cut["dm"] = [cfg["binning_default"][0], cfg["binning_default"][1]]
nbins = cfg["binning_default"][2]

if pt_ups1 < 10:
    order = 5
elif pt_ups1 < 14:
    order = 3
else:
    order = 2
# order=2
print t.yellow("Polynom order: "), order

default_frac = 0.5

a1 = db.alphab1(bin, 1)
a2 = db.alphab1(bin, 2)
a3 = db.alphab1(bin, 3)
if not (a1 or a2 or a3):
    print t.red("No b1 fraction informaition for the bin")
frac = (a1 if a1 else 0.6, a2 if a2 else 0.5, a3 if a3 else 0.5)
# frac = (0.6, 0.5, 0.5)
print t.yellow("current b1 fractions: "), str(frac)


sfracs = _sfracs(cut["pt_ups"])
if sfracs:
    print t.yellow("MC sigma[chi_b1(1P)]: "), sfracs[0]
    print t.yellow("MC sigma[chi_b1(2P)]/sigma[chi_b1(1P)]: "), sfracs[1]
    print t.yellow("MC sigma[chi_b1(3P)]/sigma[chi_b1(1P)]: "), sfracs[2]
else:
    print t.red("No MC sigma informaition for the bin")
# sfracs=None

has_3p = True if pt_ups1 >= 12 else False
print t.yellow("Has chib(3P): "), has_3p


tuples_file = cfg["tuples%d" % year]
tuples = ROOT.TChain("ChibAlg/Chib")
tuples.Add(tuples_file)

canvas.SetTitle("%d-%s %d" % (pt_ups1, pt_ups2, year))

# Width from database
mc_width = []
model = ChibModel(canvas=canvas,
                  dm_begin=cut["dm"][0],
                  dm_end=cut["dm"][1],
                  nbins=nbins,
                  bgorder=order,
                  frac=frac,
                  sfracs=sfracs,
                  has_3p=has_3p)

if cut["dm"][0] >= 0.6:
    model.n1p.fix(0)
    model.chib1p.mean1.setConstant(True)
    model.chib1p.sigma1.setConstant(True)

if "fixed_means" in cfg:
    # fix_means = (4.3150e-01, 7.9379e-01, 1.0692e+00)
    # fix_means = (4.2993e-01, 8.0603e-01, 1.0907e+00)
    fix_means = cfg["fixed_means"]

    print t.yellow("Fix means to:"), str(fix_means)
    if fix_means[0]:
        model.chib1p.mean1.fix(fix_means[0])
    if fix_means[1]:
        model.chib2p.mean1.fix(fix_means[1])
    if fix_means[2]:
        model.chib3p.mean1.fix(fix_means[2])


f = fit.Fit(model=model,
            tuples=tuples,
            cut=cut,
            field="dm",
            is_unbinned=cfg["is_unbinned"],
            nbins=nbins,
            has_splot=cfg["has_splot"])
f.year = str(year)
f.process()
print f
