import shelve

from lib import utils
from lib import pdg
from AnalysisPython.PyRoUts import VE
from IPython import embed as shell  # noqa


class DB(object):
    def __init__(self, chib="chib1s", ups="ups", mc="mc_1s", iups=1):
        self.chib_path = "data/%s.db" % chib if chib else None
        self.ups_path = "data/%s.db" % ups if ups else None
        self.mc_path = "data/%s.db" % mc if mc else None
        self.iups = iups

        self.chib = shelve.open(self.chib_path, "r") if chib else None
        self.ups = shelve.open(self.ups_path, "r") if ups else None
        self.mc = shelve.open(self.mc_path, "r") if mc else None

    def eff(self, bin, np, nb=None, ns=1):
        if (not bin in self.mc["fits"]) or (not bin in self.mc["u%ds" % ns]):
            return None

        chib = self.mc["fits"][bin]
        us = self.mc["u%ds" % ns][bin]

        keys = ("cb1%d" % np, "cb2%d" % np)
        if nb:
            cb = VE(str(chib[keys[nb - 1]]["N"]))
            ups = us[keys[nb - 1]]
            return cb / ups
        else:
            values = []
            for k in keys:
                cb = VE(str(chib[k]["N"]))
                ups = us[k]
                values.append(cb / ups)
            return utils.new_ve(values[0], values[1])

    def frac(self, year, bin, np, ns=1):
        n_chib = self.nchib(year, bin, np)
        n_ups = self.nups(year, bin, ns)
        e = self.eff(bin=bin, np=np, ns=ns)
        return (n_chib / e) / n_ups

    def nchib(self, year, bin, np):
        key = "N%dP" % np
        if not key in self.chib[year][bin]:
            return None
        return VE(str(self.chib[year][bin][key]))

    def nups(self, year, bin, ns):
        return VE(str(self.ups[year][bin]["N%dS" % ns]))

    def crossb2b1(self, bin):
        data = {
            (6, 8): VE(1.775, 0.175 ** 2),
            (8, 10): VE(1.5, 0.1 ** 2),
            (10, 12): VE(1.3, 0.1 ** 2),
            (12, 14): VE(1.15, 0.05 ** 2),
            (14, 18): VE(1.05, 0.05 ** 2),
            (18, 22): VE(0.95, 0.05 ** 2),
            (22, 30): VE(0.85, 0.05 ** 2),
            (18, 30): VE(0.9, 0.1 ** 2)
        }
        return data[bin] if bin in data else None

    def ratiob2b1(self, bin, np):
        branching = [pdg.BR21_Y1S / pdg.BR11_Y1S,
                     pdg.BR22_Y1S / pdg.BR12_Y1S,
                     pdg.BR22_Y1S / pdg.BR12_Y1S
                     ]
        eff_b2 = self.eff(bin, np, 2)
        eff_b1 = self.eff(bin, np, 1)
        
        if (eff_b2 is None) or (eff_b1 is None):
            return None
        
        eff = eff_b2 / eff_b1
        cross = self.crossb2b1(bin)
        return cross * branching[np - 1] * eff

    def alphab1(self, bin, np):
        r = self.ratiob2b1(bin, np)
        return 1.0 / (1.0 + r) if r is not None else None

    def mcfit(self, bin, np, nb):
        return self.mc["fits"][bin]["cb%d%d" % (nb, np)]

    def fit(self, year, bin):
        return self.chib[year][bin]

    def upsfit(self, year, bin):
        return self.ups[year][bin]
