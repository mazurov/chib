#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 1024, 768)

import types
import sys
from lib import utils
from lib import fit
from lib.chibmc3s import ChibMCModel
from AnalysisPython.PyRoUts import VE
from lib.graph import Graph, MultiGraph

from IPython import embed as shell  # noqa
from ext.blessings import Terminal
t = Terminal()

import shelve
from collections import defaultdict


def save(result):
    db = shelve.open('data/mc_3s_prob.db')
    fits = db.get("fits", {})
    for b in result.keys():
        bn = fits.get(b, {})
        bn.update(result[b])
        fits[b] = bn
    # fits.update(dict(result))

    db["fits"] = fits
    print db["fits"]
    db.close()



cfg = utils.json("configs/mcfits3s.json")

# binning = [(18, None), (18, 22), (22, 30)]
binning = [(27, None)]

tuples = ROOT.TChain("ChibAlg/Chib")
tuples.Add(cfg["tuples"])

basic_cut = utils.cut_expr(cfg["cut"])
print t.yellow("Basic cut:"), basic_cut

db = shelve.open("data/mc_elist3s.db")
mc_elist = db.get("elist", None)
if True:
# if not mc_elist:
    tuples.Draw(">>mc_elist", basic_cut, "entrylist")
    mc_elist = ROOT.gROOT.FindObject("mc_elist")
    db["elist"] = mc_elist
db.close()

tuples.SetEntryList(mc_elist)
# ============================================================================
# shell()
# sys.exit(0)
# ============================================================================

result = defaultdict(dict)

p=3
for b in range(1, 3):
    name = "chib{b}({p}P)".format(b=b, p=p)
    x1, x2, nbins = cfg["xaxis"]
    model = ChibMCModel(canvas=canvas, p=p, b=b,
                        dm_begin=x1,
                        dm_end=x2,
                        nbins=nbins
                        )
    # model.chib.sigma.fix(0.0205)
    cut = {"np": p, "nb": b, "dmplusm3s": [x1, x2]}
    for bin in binning:
        # model.user_labels = user_labels(bin[0], bin[1])
        cut["pt_ups"] = bin
        f = fit.Fit(model=model,
                    tuples=tuples,
                    cut=cut,
                    field="dmplusm3s",
                    has_splot=True,
                    is_unbinned=cfg["is_unbinned"],
                    nbins=nbins
                    )
        db_key = "cb%d%d" % (b, p)
        image_name = "%s_%d_%s" % (db_key, bin[0], str(bin[1]))
        f.process()
        # shell()
        is_good = f.run()
        print f.model
        if not is_good:
            print t.red("Bad fit:"), name
            shell()
        shell()
        result[bin][db_key] = model.params()
        model.save_image("figs/mc/fits3s/%s.pdf" % image_name)
print result