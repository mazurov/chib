tree = f.data.tree()

hists = [
    ROOT.TH1D("h_B", "B", 100, 0.6, 4),
    ROOT.TH1D("h_N1P", "N1P", 100, 0.6, 4),
    ROOT.TH1D("h_N2P", "N2P", 100, 0.6, 4),
    ROOT.TH1D("h_N3P", "N3P", 100, 0.6, 4)
]

hists[0].SetLineColor(ROOT.kBlue)
hists[0].SetMarkerColor(ROOT.kBlue)

hists[1].SetLineColor(ROOT.kRed)
hists[1].SetMarkerColor(ROOT.kRed)

hists[2].SetLineColor(ROOT.kCyan)
hists[2].SetMarkerColor(ROOT.kCyan)

hists[3].SetLineColor(ROOT.kGreen)
hists[3].SetMarkerColor(ROOT.kGreen)

for h in hists:
    h.Sumw2()
    tree.Draw("pt_g >> h_%s" % h.GetTitle(), "%s_sw" % h.GetTitle())
    h.Scale(1.0 / h.Integral())

hists = sorted(hists, key=lambda h: -h.GetMaximum())

opts = ""
for h in hists:
    h.Draw(opts)
    opts = "same"
