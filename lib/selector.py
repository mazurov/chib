import ROOT
from AnalysisPython.PySelector import Selector
from AnalysisPython.PySelector import SelectorWithCuts
from AnalysisPython.progress_bar import ProgressBar

from AnalysisPython.Logger import getLogger
logger = getLogger("Selector")

from lib import utils
from collections import namedtuple
from IPython import embed as shell


# ==============================================================================
RAD = ROOT.RooAbsData
if RAD.Tree != RAD.getDefaultStorageType():
    print 'DEFINE default storage type to be TTree! '
    RAD.setDefaultStorageType(RAD.Tree)
# =============================================================================


class UniversalSelector(SelectorWithCuts):

    def __init__(self, selection, columns):
        self.selection =  utils.cut_expr(selection)
        SelectorWithCuts.__init__(self, self.selection)

        DataType = namedtuple('DataSet', columns)
        self.columns = DataType(*[ROOT.RooRealVar(name, name, 0)
                                  for name in columns])

        aset = ROOT.RooArgSet("args")
        for c in self.columns:
            aset.add(c)
        self.varset = ROOT.RooArgSet(aset)
        self.data = ROOT.RooDataSet("ds", "ds", self.varset)

        self.events = 0
        self.progress = None

    def dataset(self):
        return self.data

    # the only one important method
    def Process(self, entry):
        if self.GetEntry(entry) <= 0:
            return 0

        if not self.progress:
            self.total = self.fChain.Draw("m", self.selection)
            logger.info('TChain entries: %d' % self.total)
            self.progress = ProgressBar(
                0,
                self.total,
                80,
                mode='fixed'
            )

        if 0 == self.events % 1000:
            self.progress.increment_amount(1000)
            print self.progress, '\r',

        self.events += 1

        tuple = self.fChain
        for c in self.columns:
            c.setVal(getattr(tuple, c.GetName()))

        self.data.add(self.varset)
        return 1
