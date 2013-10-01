#!/usr/bin/env ipython
import ROOT
import AnalysisPython.PyRoUts as RU

tuples = [ROOT.TChain("ChibAlg/Chib"), ROOT.TChain("ChibAlg/Chib")]

for i in range(2):
    tuples[i].Add("data/chib201%d_v2.root" % (i+1))

axis = range(1, 11)
hists = [RU.h1_axis(axis),  RU.h1_axis(axis)]

for i in range(2):
    same = "same" if i == 1 else ""
    tuples[1-i].Draw('perevent >> %s' % hists[i].GetName(), "", same)
