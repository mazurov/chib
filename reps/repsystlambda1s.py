#!/usr/bin/env ipython
# ============================================================================
# Input
# ============================================================================

YEAR = "2012"
# Reference database
REF = "data/chib1s_tr.db"

# Parameters database chib1s_l0<0.l>.db
PARAM = ["data/chib1s_l0%d.db" % i for i in range(10)] + ["data/chib1s_l1.db"]

BINNINGS = [
    [(6, 8), (8, 10), (10, 12), (12, 14)],[(14, 18), (18, 22),  (22, 30), (18, 30)]]
# BINNINGS = [[(6, 8), (8, 10)]]
# ============================================================================
# Imports
# ============================================================================
import shelve
from lib import utils
from lib import tmpl
# ============================================================================
renderer = tmpl.renderer()
# ============================================================================
# Main
# ============================================================================
print renderer.render_name("systlambda1s-head", {})
# ============================================================================
db_ref = shelve.open(REF, "r")[YEAR]
for binning in BINNINGS:
    bins = ""
    keys = ""
    lines = ""

    ll = 3
    for bin in binning:
        bins += " & & \multicolumn{3}{c}{$%s < p_T < %s \gevc$}" % bin
        keys  += " & & $N_{\chibOneP}$ & $N_{\chibTwoP}$ & $N_{\chibThreeP}$"
        lines += "\cmidrule{%d-%d}" % (ll, ll+2)
        ll += 4

    alignment = "rrrr" * len(binning)

    rows = []
    for i, l in enumerate(utils.drange(0, 1, 0.1)):
        rows.append("%.1f " % l)
        db_lambda = shelve.open(PARAM[i], "r")[YEAR]
        for bin in binning:
            rows[i] += " & "
            for np in range(1, 4):
                key = "N%dP" % np
                if key in db_ref[bin]:
                    ref, cur = db_ref[bin][key][0], db_lambda[bin][key][0]
                    change = round(100 - cur * 100 / ref, 0)
                    rows[i] += " & %d" % change
                else:
                    rows[i] += " & - "

    context = {
        "bins": bins,
        "alignment": alignment,
        "cols": 4*len(binning),
        "keys": keys,
        "lines": lines,
        "rows": "\\\\\n".join(rows)
    }

    print ("\subtable[$%d < p_T < %d \gevcc$]{" %
        (binning[0][0], binning[-1][1]) if len(BINNINGS) > 1 else "")
    print renderer.render_name("systlambda1s", context)
    print ("}" if len(BINNINGS) > 1 else "")

print renderer.render_name("systlambda1s-foot", context)