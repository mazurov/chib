#!/usr/bin/env ipython
import ROOT
import shelve

file = "data/mc11a_v3.root"

tuples = ROOT.TChain("ChibAlg/Chib")
tuples.Add(file)

db = shelve.open("data/mc_explorer.db")

# basic_cut = "true_cb_ups1s==1 && true_cb_ups1s_y==1 && true_cb_ups1s_g==1"
basic_cut = "true_cb_ups2s==1 && true_cb_ups2s_y==1 && true_cb_ups2s_g==1 && "
if (file not in db) or (basic_cut not in db[file]):
    file_dict = db.get(file, {})
    tuples.Draw(">>mc_list", basic_cut, "entrylist")
    mc_list = ROOT.gROOT.FindObject("mc_list")
    file_dict[basic_cut] = mc_list
    db[file] = file_dict
else:
    mc_list = db[file][basic_cut]

tuples.SetEntryList(mc_list)
