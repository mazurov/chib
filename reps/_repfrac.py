#!/usr/bin/env ipython
import ROOT
from lib import utils
from lib import graph

import shelve
from collections import defaultdict

db_mc = shelve.open("data/mc.db")
db_cb = shelve.open("data/chib1s_alpha.db")
db_ups = shelve.open("data/ups.db")

binning1 = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 22), (22, 30)]
binning2 = [(6, 8), (8, 10), (10, 12), (12, 14), (14, 18), (18, 30)]
energy = {"2011": 7, "2012": 8}

values = {"2011": defaultdict(list), "2012": defaultdict(list)}
for year in ["2011", "2012"]:
    db_cb_year = db_cb[year]
    db_ups_year = db_ups[year]
    for ip in range(3):
        if ip==0:
            binning = binning1
        else:
            binning = binning2
        result = """\\begin{table}[H]
\\caption{\\small \\sqs = %d \\tev. Fraction of \\OneS produced in $\\chi_b(%dP)$ decay}
\\scalebox{0.7}{
\\begin{tabular}{l%s}
%% \\hline \\hline
& \\multicolumn{%d}{c}{\\OneS transverse momentum interval in \\gevc} \\\\
""" % (energy[year], ip+1,"c"*len(binning), len(binning)-1)
        result += " %s \\\\\n\\hline\n" % reduce(lambda acc, bin: acc+" & %d - %d" % bin,
                              binning,"")
        result += "$N_{\chi_b(%dP)}$ " % (ip+1)
        for bin in binning:
            db_cb_bin = db_cb_year[bin]
            key = "N%dP" % (ip+1)
            if key in db_cb_bin:
                result += " & %s" %  utils.latex_ve_pair(db_cb_bin[key])
            else:
                result += " & --- "
        result += "\\\\\n"
        result += "$N_{\Y1S}$ "
        for bin in binning:
            db_cb_bin = db_cb_year[bin]
            db_ups_bin = db_ups_year[bin]
            cb_key = "N%dP" % (ip+1)
            if key in db_cb_bin:
                result += " & %s" %  utils.latex_ve_pair(db_ups_bin["N1S"])
            else:
                result += " & --- "
        result += "\\\\\n"        
        result += "$\\eps_{\chi_b(%dP)}^{MC}$ (\\%%) " % (ip+1)
        for bin in binning:
            db_cb_bin = db_cb_year[bin]
            cb_key = "N%dP" % (ip+1)
            if key in db_cb_bin:
                result += " & %s" %  utils.latex_ve(utils.eff(db_mc=db_mc,
                    bin=bin, np=ip+1)*100)
            else:
                result += " & --- "
        result+= "\\\\\n"
        # result+= "\\hline\n"
        result += "\\rule{0pt}{4ex}Fraction (\\%) "
        for bin in binning:
            db_cb_bin = db_cb_year[bin]
            cb_key = "N%dP" % (ip+1)
            if key in db_cb_bin:
                v = utils.frac(
                        year=year,
                        db_chib=db_cb,
                        db_ups=db_ups,
                        db_mc=db_mc,
                        bin=bin,
                        np=ip+1)*100
                values[year]["cb%d" % (ip+1)].append((bin, v))
                result += " & %s" % utils.latex_ve(v)
            else:
                result += " & --- "
        result+= "\\\\\n"
        result+= "%\\hline\\hline\n"
        result+="\\end{tabular}\n"
        result+="}\n"
        result+="\\label{tab:frac_cb%d_u1s}\n" % (ip+1)
        result+="\\end{table}\n"
        print result

colors = {"2011": ROOT.kBlue, "2012": ROOT.kRed}
markers = {"2011": ROOT.kFullSquare, "2012": ROOT.kFullCircle}
mgraphs = []
print values
for ip in range(3):
    graphs = []
    for year in ["2011", "2012"]:
        g = graph.Graph(values=values[year]["cb%d" % (ip+1)],
                        color=colors[year],
                        marker=markers[year]
                        )
        graphs.append(g)
    mg = graph.MultiGraph(graphs=graphs)
    mgraphs.append(mg)
    mg.draw()