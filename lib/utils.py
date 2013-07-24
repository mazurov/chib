# -*- coding: utf-8 -*-
import AnalysisPython.PyRoUts as RU

import re
import simplejson

from IPython import embed as shell  # noqa

import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')


def cut_expr(fields):
    result = ""
    prefix = ""
    for field in fields:
        if isinstance(fields[field], tuple) or isinstance(fields[field], list):
            low, high = fields[field]
            if low is not None:
                result += " %s %s > %.4f" % (prefix, field, low)
                prefix = "&&"
            if high is not None:
                result += " %s %s < %.4f" % (prefix, field, high)
                prefix = "&&"
        else:
            result += " %s %s == %.0f" % (prefix, field, fields[field])
            prefix = "&&"
    return result


def check_select(tup, cuts):
    # TODO: fix this hack. Need for streeping
    if not ((int(tup.Ups_l0tos) & 2) == 2 and (int(tup.Ups_l1tos) & 2) == 2 and
           (int(tup.Ups_l2tos) & 2) == 2):
        return False

    for field in [x for x in cuts if x[0] != '(']:
        value = getattr(tup, field)
        if isinstance(cuts[field], tuple) or isinstance(cuts[field], list):
            low, high = cuts[field]
            if (low is not None) and (value < low):
                return False
            if (high is not None) and (value > high):
                return False
        else:
            if value != cuts[field]:
                return False

    return True


def drange(start, stop, step):
    r = start
    while r <= stop:
        yield r
        r += step


def json(file):
    return simplejson.load(open(file, "r"))


def sconfig(str):
    return json.loads(str)


def is_good_fit(fit):
    return fit.covQual() == 3


# def str_ve(ve, sig=None):
#     f = '{0:' + (('.%d' % sig) if sig is not None else '') + 'f}'
#     return f.format(ve.value()) + "±" + f.format(ve.error())


# def latex_ve(ve, sig=None):
#     f = '{0:' + (('.%d' % sig) if sig is not None else '') + 'f}'
#     return f.format(ve.value()) + "$\pm$" + f.format(ve.error())


# def latex_ve(ve, prec=1):
#     grouping = ve.value() > 9999
#     v = locale.format("ve.value()", grouping=grouping)


def mass_ytitle(yaxis):
    res = re.findall(
        r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', yaxis.GetTitle())
    yaxis.SetTitle("Candidates / ( %.0f MeV/c^{2} )" % (
        float(res[0][0]) * 1000))
    # yaxis.SetTitleOffset(1.2)


def pdg_round(ve):
    value = ve.value()
    error = ve.error()
    "Given a value and an error, round and format them according to the PDG rules for significant digits"
    def threeDigits(value):
        "extract the three most significant digits and return them as an int"
        return int(("%.2e" % float(error)).split('e')[0].replace('.', '').replace('+', '').replace('-', ''))

    def nSignificantDigits(threeDigits):
        assert threeDigits < 1000, "three digits (%d) cannot be larger than 10^3" % threeDigits
        if threeDigits < 101:
            return 2  # not sure
        elif threeDigits < 356:
            return 2
        elif threeDigits < 950:
            return 1
        else:
            return 2

    def frexp10(value):
        "convert to mantissa+exp representation (same as frex, but in base 10)"
        valueStr = ("%e" % float(value)).split('e')
        return float(valueStr[0]), int(valueStr[1])

    def nDigitsValue(expVal, expErr, nDigitsErr):
        "compute the number of digits we want for the value, assuming we keep nDigitsErr for the error"
        return expVal - expErr + nDigitsErr

    def formatValue(value, exponent, nDigits, extraRound=0):
        "Format the value; extraRound is meant for the special case of threeDigits>950"
        roundAt = nDigits - 1 - exponent - extraRound
        nDec = roundAt if exponent < nDigits else 0
        if nDec < 0:
            nDec = 0
        grouping = value > 9999
        return locale.format('%.' + str(nDec) + 'f',round(value, roundAt), grouping=grouping)

    tD = threeDigits(error)
    nD = nSignificantDigits(tD)
    expVal, expErr = frexp10(value)[1], frexp10(error)[1]
    extraRound = 1 if tD >= 950 else 0
    return (
            formatValue(value, expVal, nDigitsValue(
            expVal, expErr, nD), extraRound),
        formatValue(error, expErr, nD, extraRound))


def latex_ve(ve):
    value, error = pdg_round(ve)
    if error != "0.0":
        return "%s $\pm$ %s" % (value, error)
    else:
        return "%s" % value


def latex_ve_pair(p):
    return latex_ve(RU.VE(str(p)))


def long_format(val):
    grouping = val > 9999
    return locale.format("%d", val, grouping=grouping)

def new_ve(*lst):
    l = []
    for v in lst:
        l.append(v.value()+v.error())
        l.append(v.value()-v.error())
    a,b = min(l), max(l)
    err = (b-a)/2.0
    return RU.VE(a+err, err**2)

def eff(db_mc, bin, np, nb=None):
    db_chib = db_mc["fits"][bin]
    db_u1s = db_mc["u1s"][bin]
    keys = ("cb1%d" % np, "cb2%d" % np)
    if nb:
        cb = RU.VE(str(db_chib[keys[nb-1]]["N"]))
        ups = db_u1s[keys[nb-1]]
        return cb / ups
    else:
        values = []
        for k in keys:
            cb = RU.VE(str(db_chib[k]["N"]))
            ups = db_u1s[k]
            values.append(cb/ups)
        return new_ve(values[0], values[1])

def frac(year, db_chib, db_ups, db_mc, bin, np, ns=1):
    n_chib = RU.VE(str(db_chib[year][bin]["N%dP" % np]))
    n_ups = RU.VE(str(db_ups[year][bin]["N%dS" % ns]))
    e = eff(db_mc=db_mc, bin=bin, np=np)
    return (n_chib/e)/n_ups