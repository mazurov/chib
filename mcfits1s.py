#!/usr/bin/env ipython
import ROOT
canvas = ROOT.TCanvas("c1", "c1", 1024, 768)

import types
import sys
import os.path
from lib import utils
from lib import fit
from lib.chibmc import ChibMCModel
from AnalysisPython.PyRoUts import VE
from lib.graph import Graph, MultiGraph

from IPython import embed as shell  # noqa
from ext.blessings import Terminal
t = Terminal()

import shelve
from collections import defaultdict


def user_labels(pt_ups1, pt_ups2):
    def _user_labels(self):
        if pt_ups2 is not None:
            txt = "%d < p_{T}^{#Upsilon(1S)} < %d GeV/c" % (pt_ups1, pt_ups2)
        else:
            txt = "p_{T}^{#Upsilon(1S)} > %d GeV/c" % pt_ups1
        self.user_label = ROOT.TLatex(0.55, 0.85, txt)
        self.user_label.SetNDC()
        self.user_label.Draw()
    return _user_labels

# mc_mass - pt_g > 1.3


def save(result, name):
    db = shelve.open('data/%s.db' % name)
    fits = db.get("fits", {})

    fits.update(dict(result))

    db["fits"] = fits
    db.close()


# def graphs(result):
#     values1 = defaultdict(list)
#     values2 = defaultdict(list)
#     for bin, v in sorted(result.items()):
#         for k in ["sigma", "ar", "nr", "al", "nl"]:
#             if k not in result[bin]["chib13p"]:
#                 continue
#             val = result[bin]["chib13p"][k]
#             if isinstance(val, tuple):
#                 values1[k].append((bin, VE(val[0], val[1] ** 2)))
#             val = result[bin]["chib23p"][k]
#             if isinstance(val, tuple):
#                 values2[k].append((bin, VE(val[0], val[1] ** 2)))

#     mgraphs = []
#     for k in values1:
#         graph1 = Graph("b1", ROOT.kBlue, values1[k])
#         graph2 = Graph("b2", ROOT.kRed, values2[k])
#         mg = MultiGraph(title=k, xtitle="bin", ytitle=k,
#                         graphs=[graph1, graph2], show_legend=False)
#         mg.draw("figs/mc/params/chib3p_%s.pdf" % k)
#         mgraphs.append(mg)
#     return mgraphs


cfg = utils.json("configs/mcfits1s.json")

binning = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 30), (18, 22),
           (22, 30), (14, None)]

# binning = [(18,30)]


tuples = ROOT.TChain("ChibAlg/Chib")
tuples.Add(cfg["tuples"])

basic_cut = utils.cut_expr(cfg["cut"])
print t.yellow("Basic cut:"), basic_cut

db = shelve.open("data/mc_elist.db")
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
for p in range(1, 4):
    for b in range(1, 3):
        name = "chib{b}({p}P)".format(b=b, p=p)
        x1, x2, nbins = cfg["xaxis"][p - 1]
        model = ChibMCModel(canvas=canvas, p=p, b=b,
                            dm_begin=x1,
                            dm_end=x2,
                            nbins=nbins
                            )
        # model.chib.sigma.fix(0.0205)
        cut = {"np": p, "nb": b, "dmplusm1s": [x1, x2]}
        for bin in binning:
            # model.user_labels = user_labels(bin[0], bin[1])
            cut["pt_ups"] = bin
            f = fit.Fit(model=model,
                        tuples=tuples,
                        cut=cut,
                        field="dm",
                        has_splot=True,
                        is_unbinned=cfg["is_unbinned"],
                        nbins=nbins
                        )
            db_key = "cb%d%d" % (b, p)
            f.process()
            # shell()
            is_good = f.run()
            print f.model
            if not is_good:
                print t.red("Bad fit:"), name
                shell()

            result[bin][db_key] = model.params()

            # model.save_image("figs/mc/fits/%s.pdf" % image_name)
            image_name = "%s_%d_%s.pdf" % (db_key, bin[0], str(bin[1]))
            utils.savemcfit(result, model.canvas, cfg["name"], image_name)

print result
