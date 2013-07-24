import ROOT
import AnalysisPython.PyRoUts as RU


class Graph(object):

    def __init__(self, color, marker, values, title=""):
        self.color = color
        self.marker = marker
        self.title = title
        self.values = values

        self.max = -1e+8
        self.min = 1e+8


    def _get_axis(self):
        return [v[0][0] for v in self.values] + [self.values[-1][0][-1]]

    def get_hist(self):
        h = RU.h1_axis(
            self._get_axis(), self.title
        )
        h.SetStats(0)
        h.SetLineColor(self.color)
        h.SetMarkerColor(self.color)
        h.SetMarkerStyle(self.marker)
        h.SetLineWidth(1)
        print self._get_axis()
        for i, v in enumerate(self.values):
            if v[1] is not None:
                p = v[1]
                emax = p.value()+p.error()
                emin = p.value()-p.error()
                self.max = emax if emax > self.max else self.max
                self.min = emin if emin < self.min else self.min
                h[i + 1] = p
        return h


class MultiGraph(object):

    def __init__(self, graphs, title="", xtitle="", ytitle="", ymin=None, ymax=None,
        show_legend=False):
        self.title = title
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.graphs = graphs
        self.show_legend = show_legend

        self.hists = []
        cmin = 1e+8
        cmax = -1e+8
        for g in self.graphs:
            h = g.get_hist()
            h.SetTitle(self.title)
            # h.GetXaxis().SetTitle(self.xtitle)
            # h.GetYaxis().SetTitle(self.ytitle)

            cmin = g.min if g.min < cmin else cmin
            cmax = g.max if g.max > cmax else cmax

            if ymin is not None:
                h.SetMinimum(ymin)
            if ymax is not None:
                h.SetMaximum(ymax)
            self.hists.append(h)

        if not ymin:
            for i, h in enumerate(self.hists):
                h.SetMinimum(cmin)

        if not ymax:
            for i, h in enumerate(self.hists):
                h.SetMaximum(cmax)

    def legend(self):
        self.legenda = ROOT.TLegend(0.6, 0.5, 0.9, 0.65)
        for i, h in enumerate(self.hists):
            self.legenda.AddEntry(h, self.graphs[i].title, "l")
        if self.show_legend:
            self.legenda.draw()

    def draw(self, to_file=None):
        self.canvas = ROOT.TCanvas(RU.rootID("c_"), self.title, 800, 600)
        for i, h in enumerate(self.hists):
            same = "same" if i > 0 else ""
            h.Draw(same)

        self.legend()
        if to_file:
            self.canvas.SaveAs(to_file)
