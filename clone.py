#!/usr/bin/env ipython
import ROOT
import sys
import array
from lib import utils
from lib import pdg
from ext.blessings import Terminal
t = Terminal()

cfg = utils.json("configs/chib1s.json")
year = sys.argv[1]
output = sys.argv[2]

tuples_chib = ROOT.TChain("ChibAlg/Chib")
tuples_ups = ROOT.TChain("UpsilonAlg/Upsilon")

input = cfg["tuples%s_old" % year]
tuples_chib.Add(input)
tuples_ups.Add(input)

cut = cfg["cut"]

cut["pt_ups"] = [6, None]
del cut["dm_1s"]
str_cut_chib = utils.cut_expr(cut)

# del cut["dm_1s"]
del cut["pt_g"]
del cut["lv01"]
del cut["cl_g"]

str_cut_ups = utils.cut_expr(cut)

print t.yellow("Cut on chib: %s" % str_cut_chib)
print t.yellow("Cut on ups: %s" % str_cut_ups)

tuples_chib_new = tuples_chib.CopyTree(str_cut_chib)
tuples_ups_new = tuples_chib.CopyTree(str_cut_ups)


dmplusm1s = array.array("d", [0.0])
dmplusm2s = array.array("d", [0.0])
dmplusm3s = array.array("d", [0.0])

tuples_chib_new2 = tuples_chib_new.CloneTree(0)

b_dmplusm1s = tuples_chib_new2.Branch("dmplusm1s", dmplusm1s, "dmplusm1s/D")
b_dmplusm2s = tuples_chib_new2.Branch("dmplusm2s", dmplusm2s, "dmplusm2s/D")
b_dmplusm3s = tuples_chib_new2.Branch("dmplusm3s", dmplusm3s, "dmplusm3s/D")

entries = tuples_chib_new.GetEntries()
for i in range(entries):
    tuples_chib_new.GetEntry(i)
    dm = tuples_chib_new.GetLeaf("dm").GetValue()
    dmplusm1s[0] = dm + pdg.UPS1S.value()
    dmplusm2s[0] = dm + pdg.UPS2S.value()
    dmplusm3s[0] = dm + pdg.UPS3S.value()
    tuples_chib_new2.Fill()

file = ROOT.TFile(output, "create")
file.mkdir("ChibAlg")
file.mkdir("UpsilonAlg")

file.cd("/ChibAlg")
tuples_chib_new2.Write("Chib")
file.cd("/UpsilonAlg")
tuples_ups_new.Write("Upsilon")
file.Close()
