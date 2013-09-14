#!/usr/bin/env ipython
import os
import sys
import shelve
from AnalysisPython.PyRoUts import VE
from lib import utils
from lib import pdg

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'ext')]

import pystache
renderer = pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")

db = shelve.open("data/chib1s_mass_nlong100.db", "r")
mu = ["", ""]
N = ["", ""]
B2S = ["", ""]
B = ""

context = {}
for year in ["2011", "2012", "all"]:
    fit = db[year][(14, None)]
    for i in range(2):
        mu[i] += " & " + utils.latex_ve_pair(
            VE(str(fit["mean_b1_%dp" % (i + 2)])) * 1000)
        n = VE(str(fit["N%dP" % (i + 2)]))
        N[i] += " & " + utils.latex_ve(n)
        B2S[i] += " & " + utils.latex_ve(n.b2s())
    B += " & " + utils.latex_ve_pair(VE(str(fit["B"])))

for i in range(2):
    mu[i] += " & " + utils.latex_ve_pair(pdg.DM1S[2 * (i + 1)] * 1000)
    context["mu%d" % (i + 2)] = mu[i]
    context["N%dP" % (i + 2)] = N[i]
    context["B%dP" % (i + 2)] = B2S[i]

context["B"] = B

print renderer.render_name("mass", context)
