#!/usr/bin/env ipython
from lib import tmpl
from lib.db import DB
from lib import utils

NS = 3

if NS == 1:
    NP = 1
    BINNING = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22),
               (22, 30), (18, 30)]

if NS == 2:
    NP = 2
    BINNING = [(18, 22), (22, 40)]

if NS == 3:
    NP = 3
    BINNING = [(27, 40)]

db = DB(mc="mc_%ds_prob" % NS)
renderer = tmpl.renderer()

prefix = " & "
context = tmpl.bins(BINNING)

for np in range(NP, 4):
    b = ["", ""]
    yb = ["", ""]
    eb = ["", ""]
    eff = ""

    for bin in BINNING:
        for nb in range(1, 3):
            fit = db.mcfit(bin=bin, np=np, nb=nb)
            b[nb - 1] += tmpl.col(utils.latex_ve_pair(fit["N"]))
            yb[nb - 1] += tmpl.col(
                utils.long_format(db.mcups(bin=bin, np=np, nb=nb, ns=NS)))
            eb[nb - 1] += tmpl.col(
                utils.latex_ve_pair(db.eff(bin, np=np, nb=nb, ns=NS) * 100))
        eff += tmpl.col(
            utils.latex_ve_pair(db.eff(bin, np=np, ns=NS) * 100), bold=True)

    context.update({
        "np": np,
        "ns": NS,
        "b1": b[0],
        "b2": b[1],
        "yb1": yb[0],
        "yb2": yb[1],
        "eb1": eb[0],
        "eb2": eb[1],
        "eff": eff,
    })
    print renderer.render_name("mceff", context)
