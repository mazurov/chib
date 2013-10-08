#!/usr/bin/env ipython
# ============================================================================
# Input
# ============================================================================

YEAR = "2012"
# Reference database
REF = "data/chib2s_tr.db"


# Parameters database chib1s_l0<0.l>.db
PARAM = ["data/chib2s_min3p.db", "data/chib2s_max3p.db"]

BINNINGS = [[(18, 25), (25, 40)]]
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
print renderer.render_name("systm3p2s-head", {})
# ============================================================================
db_ref = shelve.open(REF, "r")[YEAR]
for binning in BINNINGS:
    bins = ""
    keys = ""
    lines = ""

    ll = 3
    for bin in binning:
        bins += " & & \multicolumn{2}{c}{$%s < p_T < %s \gevc$}" % bin
        keys += " & & $N_{\chibTwoP}$ & $N_{\chibThreeP}$"
        lines += "\cmidrule{%d-%d}" % (ll, ll + 1)
        ll += 3

    alignment = "rrr" * len(binning)

    rows = []
    for i in range(2):
        db_m = shelve.open(PARAM[i], "r")[YEAR]
        prefix = "min" if i == 0 else "max"
        rows.append("%.3f \\gevcc ($%s\\left[m(\chiboneThreeP)\\right]$)" %
                   (db_m[binning[0]]["mean_b1_2p"] +
                    db_m[binning[0]]["dm_b13p_b12p"], prefix))

        for bin in binning:
            rows[i] += " & "
            for np in range(2, 4):
                key = "N%dP" % np
                if key in db_ref[bin]:
                    ref, cur = db_ref[bin][key][0], db_m[bin][key][0]
                    change = round(100 - cur * 100 / ref, 0)
                    rows[i] += " & %d" % change
                else:
                    rows[i] += " & - "

    context = {
        "bins": bins,
        "alignment": alignment,
        "cols": 3 * len(binning),
        "keys": keys,
        "lines": lines,
        "rows": "\\\\\n".join(rows)
    }

    print("\subtable[$%d < p_T < %d \gevcc$]{" %
         (binning[0][0], binning[-1][1]) if len(BINNINGS) > 1 else "")
    print renderer.render_name("systm3p2s", context)
    print("}" if len(BINNINGS) > 1 else "")

print renderer.render_name("systm3p2s-foot", context)
