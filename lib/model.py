import ROOT
from lib import utils
from IPython import embed as shell  # noqa
import re
NUMCPU = 2


class AbstractModel(object):
    def __init__(self, canvas, x0, x1, xfield, x=None, nbins=100,
                 user_labels=None):
        self.x0 = x0
        self.x1 = x1
        self.xfield = xfield
        self.x = x if x else ROOT.RooRealVar(xfield, xfield, x0, x0, x1)
        self.nbins = nbins
        self.canvas = canvas

        self.chi2 = -1
        self.fit = None
        self.frame = None
        self.user_labels = user_labels

        self.splots = []

    def fitHisto(self, histo, *args):
            """
            Fit the histogram
            """
            self.lst = ROOT.RooArgList(self.x)
            self.imp = ROOT.RooFit.Import(histo)
            self.hset = ROOT.RooDataHist(
                "ds", "Data set for histogram '%s'" % histo.GetTitle(),
                self.lst, self.imp)

            self.fit = self.pdf.fitTo(self.hset, ROOT.RooFit.Save(), *args)

            self.frame = self.x.frame()
            self.hset.plotOn(self.frame)
            self.after_fit()

    def fitTo(self, dataset, *args):
        self.dataset = dataset
        self.fit = self.pdf.fitTo(dataset,
                                  ROOT.RooFit.Save(),
                                  ROOT.RooFit.NumCPU(NUMCPU),
                                  *args
                                  )

        self.frame = self.x.frame()
        dataset.plotOn(self.frame, ROOT.RooFit.Binning(self.nbins))
        self.after_fit()
    
    def after_fit(self):
        self._plot()
        self._eval_chi2()
        self._fit_status()
        self.labels()
        if self.user_labels:
            self.canvas.cd(1)
            self.user_labels(self)
            self.canvas.cd()

    def labels(self):
        assert False, "Labels don't implemented"
        pass

    def curves(self):
        assert False, "Curves don't implemented"
        pass
    
    def draw_after(self):
        pass

    def _plot(self):
        frame = self.frame
        self.pdf.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed))
        self.curves()
        frame.drawAfter("model_Norm[%s]" % self.xfield, "h_ds")
        frame.drawAfter("model_Norm[%s]_Comp[bg]" % self.xfield, "h_ds")
        self.draw_after()        
        self.hpull = frame.pullHist("h_ds",
                                    "model_Norm[%s]" % self.xfield
                                    )


        frame_pull = self.x.frame(ROOT.RooFit.Title("Pull Distribution"))

        frame_pull.SetMinimum(-5)
        frame_pull.SetMaximum(5)
        frame_pull.SetNdivisions(8, "y")
        frame_pull.SetNdivisions(0, "x")
        frame_pull.GetYaxis().SetLabelSize(0.1)
        frame_pull.GetXaxis().SetTitle("")                                    
        frame_pull.addPlotable(self.hpull, "P")

        self.canvas.Clear()
        self.canvas.Divide(1, 2)

        pad = self.canvas.cd(1)
        pad.SetPad(0, 0.2, 1, 1)
        frame.Draw()

        pad = self.canvas.cd(2)
        # pad.SetGridy(True)
        pad.SetPad(0, 0, 1, 0.18)

        xMin = frame_pull.GetXaxis().GetXmin()
        xMax = frame_pull.GetXaxis().GetXmax()
        self.hpull_uppLine = ROOT.TLine(xMin,  3, xMax,  3)
        self.hpull_midLine = ROOT.TLine(xMin,  0, xMax,  0)
        self.hpull_lowLine = ROOT.TLine(xMin, -3, xMax, -3)
        self.hpull_uppLine.SetLineColor(ROOT.kBlue)
        self.hpull_midLine.SetLineColor(ROOT.kRed)
        self.hpull_lowLine.SetLineColor(ROOT.kBlue)
        self.hpull_uppLine.SetLineWidth(2)
        self.hpull_midLine.SetLineWidth(2)
        self.hpull_lowLine.SetLineWidth(2)
        # self.hpull_uppLine.SetLineStyle(ROOT.kDashed),
        # self.hpull_lowLine.SetLineStyle(ROOT.kDashed),


        frame_pull.Draw()
        self.hpull_uppLine.Draw()
        self.hpull_midLine.Draw()
        self.hpull_lowLine.Draw()

        self.frame_pull = frame_pull
        self.canvas.cd()

    def _eval_chi2(self):
        self.chi2 = self.frame.chiSquare("model_Norm[%s]" % self.xfield,
                                         "h_ds",
                                         len(self.fit.params()))

    def _fit_status(self):
        self.status = utils.is_good_fit(self.fit)

    def candidates(self):
        yaxis = self.frame.GetYaxis()
        res = re.findall(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                         yaxis.GetTitle())
        yaxis.SetTitle("Candidates / ( %.0f MeV/c^{2} )" %
                       (float(res[0][0]) * 1000))

    def params(self):
        return dict(
            [(p.GetName(), (p.getVal(), p.getError()))
             for p in self.fit.floatParsFinal()]
            +
            [(p.GetName(), p.getVal()) for p in self.fit.constPars()]
            + [("chi2", self.chi2)]
        )

    def save_image(self, path):
        self.canvas.SaveAs(path)
    

    def __str__(self):
        result = str(self.fit)+"\n"
        result += "chi2 = %.2f" % self.chi2
        return result
