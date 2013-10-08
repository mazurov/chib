#!/usr/bin/env ipython

# ============================================================================
from AnalysisPython.PyRoUts import VE
# ============================================================================
BINNINGS = [[(6, 8), (8, 10), (10, 12), (12, 14)],[(14, 18), (18, 22), (22, 30),
           (18, 30)]]
# BINNINGS = [[(6, 8)]]
# BINNINGS = [[(14, None)]]

# ============================================================================
import types
from lib import utils
from lib import pdg
from lib import db

import os
import sys


def mulicolumn(v, digits=2):
    fmt = "\multicolumn{2}{c}{%%.%df}" % digits
    return fmt % v

def output(year, fit, key, scale=1, digits=2, var=False):
    result = " && " if year == "2011" else " & "
    if key in fit:
        v = fit[key]
        if var or isinstance(v, types.TupleType):
            result += utils.latex_ve(VE(str(v)) * scale)
        elif year == "2011":
            result += mulicolumn(v*scale, digits)
        else:
            return ""
    else:
        result += " - "
    return result



BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'ext')]
import pystache
renderer = pystache.Renderer(escape=lambda u: u, search_dirs=["reps/tmpl"],
                             file_extension="tex")



# ============================================================================
db = db.DB(chib="chib1s_tr")
# ============================================================================
print renderer.render_name("fits1s-head", {})
for BINNING in BINNINGS:
    # ============================================================================
    alignment = "rrr" * (len(BINNING))
    # ============================================================================
    bins = ""
    for bin in BINNING:
        bins += " & & \multicolumn{2}{c}{%s}" % (
                "%s --- %s" % bin if bin[1] else "$p_T > %d \gevc$" % bin[0]
            )
    years = ""
    lines = ""

    i = 3
    for bin in BINNING:
        years += " && \sqs = 7 \\tev & \sqs = 8\\tev"
        lines += "\cmidrule{%d-%d}" % (i, i+1)
        i += 3


    N = ["", "", ""]
    B = ""
    mean = ""
    dm = ["", ""]
    dmb2b1 = ["", "", ""]
    frac = ["", "", ""]
    a = ["", "", ""]
    n = ["", "", ""]
    sigma = ""
    sigmab2b1 = ""
    sfrac = ["", ""]

    tau = ""
    phi = ["","","","",""]

    chi2 = ""
    for bin in BINNING:
        # Float parameters
        # N, mean, background, x2
        for year in ["2011", "2012"]:
            fit = db.fit(year, bin)
            prefix = " & " if year == "2012" else " && "

            key = "mean_b1_1p"
            mean += output(year, fit, key, scale=1000)

            for ip in range(3):
                key = "N%dP" % (ip + 1)
                N[ip] += output(year, fit, key)

                key = "dmb2b1_%dp" % (ip + 1)
                dmb2b1[ip] += output(year, fit, key, scale=1000, digits=2)

                key = "frac%d" % (ip + 1)
                frac[ip] += output(year, fit, key, digits=1)

                key = "a%d" % (ip + 1)
                a[ip] += output(year, fit, key, digits=2)

                key = "n%d" % (ip + 1)
                n[ip] += output(year, fit, key, digits=1)

            for ip in range(2):
                key = "dm_b1%dp_b11p" % (ip + 2)
                dm[ip] += output(year, fit, key, scale=1000, digits=0)

                key = "sfrac%dp1p" % (ip + 2)
                sfrac[ip] += output(year, fit, key)

            B += output(year, fit, "B")

            sigma += output(year, fit, "sigma_b1_1p", scale=1000)
            sigmab2b1 += output(year, fit, "sdiffb2b1")


            tau += output(year, fit, "exp_tau")

            for iphi in range(5):
                key = "poly_phi%d" % (iphi+1)
                phi[iphi] += output(year, fit, key)

            chi2 += output(year, fit, "chi2", var=True)

        context = {
            "alignment": alignment,
            "cols": 3*len(BINNING),
            "years": years,
            "lines": lines,
            "bins": bins,
            "B": B,
            "mean1": mean,
            "sigma": sigma,
            "sigmab2b1": sigmab2b1,
            "chi2": chi2,
            "tau": tau,
        }

        for ip in range(3):
            context["N%d" % (ip + 1)] = N[ip]
            context["B%d" % (ip + 1)] = B[ip]

            context["dmb2b1_%d" % (ip + 1)] = dmb2b1[ip]
            context["frac%d" % (ip + 1)] = frac[ip]
            context["a%d" % (ip + 1)] = a[ip]
            context["n%d" % (ip + 1)] = n[ip]


        for ip in range(2):
            context["dm_%d" % (ip + 2)] = dm[ip]
            context["sfrac%dp1p" % (ip + 2)] = sfrac[ip]

        for iphi in range(5):
            context["phi%d" % iphi] = phi[iphi]

    print ("\subtable[$%d < p_T^{\Y1S} < %d \gevcc$]{" % (BINNING[0][0], BINNING[-1][1]) if len(BINNINGS) > 1 else "")
    print renderer.render_name("fits1s", context)
    print ("}" if len(BINNINGS) > 1 else "")

print renderer.render_name("fits1s-foot", {})