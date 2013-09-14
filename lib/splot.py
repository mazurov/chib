import ROOT
import AnalysisPython.PyRoUts as RU

from lib import utils

from ext.blessings import Terminal
t = Terminal()


def mc_vs_data(fit):
    """ Can be called only after fit """
    cfg = utils.json("configs/splot.json")
    data_tuples = fit.data.tree()
    # if not data_tuples.GetBranch("N1P_sw"):
    #     model.sPlot(data)
    #     data_tuples = data.tree()

    mc_tuples = ROOT.TChain("ChibAlg/Chib")
    mc_tuples.Add(cfg["mc"])
    mc_cut = dict(fit.cut)

    mc_cut["true_cb_ups1s"] = 1
    mc_cut["true_cb_ups1s_y"] = 1
    mc_cut["true_cb_ups1s_g"] = 1

    mc_cut_expr = utils.cut_expr(mc_cut)
    print t.green("MC cut expression: %s") % mc_cut_expr

    mc_tuples.Draw(">>mc_elist", mc_cut_expr, "entrylist")
    mc_elist = ROOT.gROOT.Get("mc_elist")
    mc_tuples.SetEntryList(mc_elist)

    for p in cfg["parameters"]:
        param = p["name"] if not "param" in p else p["param"]
        x1, x2, nbins = p["hist"]

        for i in range(1, 4):
            name = "%s_%dp" % (p["name"], i)
            print t.green("Process %s %s" % (param, str(p)))
            h_data = RU.h(RU.hID(), name, nbins, x1, x2)
            h_data.Sumw2()
            h_data.SetLineColor(ROOT.kBlue)
            h_data.SetMarkerColor(ROOT.kBlue)
            h_data.SetMarkerStyle(ROOT.kFullSquare)

            data_tuples.Draw("{p} >> {name}".format(
                p=param, name=h_data.GetName()), "N%dP_sw" % i)
            integral = h_data.Integral()  # no events in histogram range
            if integral:
                h_data.Scale(1.0 / integral)

            h_mc = RU.h(RU.hID(), name, nbins, x1, x2)
            h_mc.Sumw2()
            h_mc.SetLineColor(ROOT.kRed)
            h_mc.SetMarkerColor(ROOT.kRed)
            h_mc.SetMarkerStyle(ROOT.kOpenCircle)

            mc_tuples.Draw(
                "{p} >> {name}".format(p=param, name=h_mc.GetName()),
                "np==%d" % i)

            integral = h_mc.Integral()  # no events in histogram range
            if integral:
                h_mc.Scale(1.0 / integral)

            hsorted = sorted(
                [h_mc, h_data], key=lambda h: h.GetMaximum(), reverse=True)
            hsorted[0].Draw()
            hsorted[1].Draw("same")

            output_path = "figs/data_vs_mc/%s.pdf" % (
                name.replace('(', '_').replace(')', '').replace(',','_'))
            fit.model.canvas.SaveAs(output_path)
# =============================================================================
