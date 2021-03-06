#!/usr/bin/env ipython

import shelve
from lib import utils

from AnalysisPython.PyRoUts import VE

db = shelve.open("data/mc_2s.db", "r")
db_chib = db["fits"]
db_u1s = db["u2s"]

binning = [(18, 22), (22, 30)]


header = """\\begin{table}[H]
\\caption{\small $\\chi_b(%dP)$ efficiency in specified  intervals of \Y2S transverse momentum.}
\\scalebox{0.7}{
\\begin{tabular}{l%s}
\multicolumn{%d}{c}{\\TwoS transverse momentum interval in \\gevc} \\\\
%s \\\\
\hline
"""

footer = """
\\end{tabular}
}
\\label{tab:mc_%s_2s_eff}
\\end{table}
"""

for np in range(2):
    table_label = "cb%d" % (np+2)
    result = header % (np+2,
                       "c"*len(binning),
                       len(binning)+1,
                       reduce(lambda acc, bin: acc+" & %d - %d" % bin,
                              binning,
                              "")
                       )
    for nb in range(2):
        if nb == 1:
            result += "\\rule{0pt}{4ex}"
        result_chib = "$N_{\chi_{b%d}(%dP)}^{MC}$" % (nb+2, np+2)
        result_ups = "$N_{\Y2S}^{MC}$"
        result_eff = "$\eps_{\chi_{b%d}(%dP)}^{MC}$ (\\%%)" % (nb+1, np+2)
        db_chib_key = "cb%d%d" % (nb+1, np+2)
        for i, bin in enumerate(binning):
            db_chib_bin = db_chib[bin]
            ve = VE(str(db_chib_bin[db_chib_key]["N"]))
            result_chib += " & %s " % utils.latex_ve(ve)

            db_ups_bin = db_u1s[bin]
            v = db_ups_bin[db_chib_key]
            result_ups += " & %s " % utils.long_format(v)

            eff = utils.eff(db_mc=db, bin=bin, np=np+2, nb=nb+1, ns=2) * 100
            result_eff += " & %s" % utils.latex_ve(eff)

        result += result_chib + "\\\\\n"
        result += result_ups + "\\\\\n"
        result += result_eff + "\\\\\n"

    result += "\\rule{0pt}{4ex}$\eps_{\chi_{b}(%dP)}^{MC}$ (\\%%)" % (np+2)
    for bin in binning:
        result += " & %s" % utils.latex_ve(utils.eff(db_mc=db, bin=bin, np=np+2, ns=2)*100)
    result += "\\\\\n"
    result += footer % table_label
    print result