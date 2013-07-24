#!/usr/bin/env ipython

import shelve
from lib import utils

from AnalysisPython.PyRoUts import VE

db = shelve.open("data/mc.db", "r")
db_chib = db["fits"]
db_u1s = db["u1s"]

binning1 = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)]
binning2 = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 30)]

header = """\\begin{table}[H]
\\caption{\small $\\chi_b(%dP)$ efficiency in specified  intervals of \Y1S transverse momentum.}
\\scalebox{0.7}{
\\begin{tabular}{l%s}
\multicolumn{%d}{c}{\\OneS transverse momentum interval in \\gevc} \\\\
%s \\\\
\hline
"""

footer = """
\\end{tabular}
}
\\label{tab:mc_%s_eff}
\\end{table}
"""

for np in range(3):
    if np == 0:
        binning = binning1
    else:
        binning = binning2

    table_label = "cb%d" % (np+1)
    result = header % (np+1,
                       "c"*len(binning),
                       len(binning)+1,
                       reduce(lambda acc, bin: acc+" & %d - %d" % bin,
                              binning,
                              "")
                       )
    for nb in range(2):
        if nb == 1:
            result += "\\rule{0pt}{4ex}"
        result_chib = "$N_{\chi_{b%d}(%dP)}^{MC}$" % (nb+1, np+1)
        result_ups = "$N_{\Y1S}^{MC}$"
        result_eff = "$\eps_{\chi_{b%d}(%dP)}^{MC}$ (\\%%)" % (nb+1, np+1)
        db_chib_key = "cb%d%d" % (nb+1, np+1)
        for i, bin in enumerate(binning):
            db_chib_bin = db_chib[bin]
            ve = VE(str(db_chib_bin[db_chib_key]["N"]))
            result_chib += " & %s " % utils.latex_ve(ve)

            db_ups_bin = db_u1s[bin]
            v = db_ups_bin[db_chib_key]
            result_ups += " & %s " % utils.long_format(v)

            eff = utils.eff(db_mc=db, bin=bin, np=np+1, nb=nb+1) * 100
            result_eff += " & %s" % utils.latex_ve(eff)

        result += result_chib + "\\\\\n"
        result += result_ups + "\\\\\n"
        result += result_eff + "\\\\\n"

    result += "\\rule{0pt}{4ex}$\eps_{\chi_{b}(%dP)}^{MC}$ (\\%%)" % (np+1)
    for bin in binning:
        result += " & %s" % utils.latex_ve(utils.eff(db_mc=db, bin=bin, np=np+1)*100)
    result += "\\\\\n"
    result += footer % table_label
    print result

header = """\\begin{table}[H]
\\caption{\small $\\chi_b(%dP)$ peak widths in specified  intervals of \Y1S transverse momentum.}
\\scalebox{0.7}{
\\begin{tabular}{l%s}
\multicolumn{%d}{c}{\\OneS transverse momentum interval in \\gevc} \\\\
%s \\\\
\hline
"""

footer = """
\\end{tabular}
}
\\label{tab:mc_%s_width}
\\end{table}
"""
for np in range(3):
    if np == 0:
        binning = binning1
    else:
        binning = binning2

    table_label = "cb%d" % (np+1)
    avg = []
    result = header % (np+1,
                       "c"*len(binning),
                       len(binning)+1,
                       reduce(lambda acc, bin: acc+" & %d - %d" % bin,
                              binning,
                              "")
                       )
    for nb in range(2):
        result_chib = "$\sigma_{\chi_{b%d}(%dP)}^{MC}$ (\mevcc)"  % (nb+1, np+1)
        db_chib_key = "cb%d%d" % (nb+1, np+1)
        for i, bin in enumerate(binning):
            db_chib_bin = db_chib[bin]
            ve = VE(str(db_chib_bin[db_chib_key]["sigma"]))
            ve *= 1000
            result_chib += " & %s " % utils.latex_ve(ve)
        result += result_chib + "\\\\\n"
    result += "\\\\\n"
    result += footer % table_label
    print result