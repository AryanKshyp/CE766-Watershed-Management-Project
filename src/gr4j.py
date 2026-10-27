"""GR4J daily rainfall-runoff model (Perrin, Michel & Andreassian 2003).

Four parameters:
    x1  production (soil) store capacity, mm
    x2  groundwater exchange coefficient, mm/day (negative = water lost to deep aquifer / outside the catchment)
    x3  routing store capacity, mm
    x4  unit-hydrograph time base, days

Inputs and outputs are in mm/day. Plain Python loop (no numba on this machine): one 39-year run is ~0.1 s.
"""
import math

import numpy as np


def _sh1(t, x4):
    if t <= 0:
        return 0.0
    return (t / x4) ** 2.5 if t < x4 else 1.0


def _sh2(t, x4):
    if t <= 0:
        return 0.0
    if t < x4:
        return 0.5 * (t / x4) ** 2.5
    if t < 2 * x4:
        return 1 - 0.5 * (2 - t / x4) ** 2.5
    return 1.0


def unit_hydrographs(x4):
    """Ordinates of UH1 (length ceil(x4)) and UH2 (length ceil(2*x4)); each sums to 1."""
    n1, n2 = math.ceil(x4), math.ceil(2 * x4)
    uh1 = [_sh1(j, x4) - _sh1(j - 1, x4) for j in range(1, n1 + 1)]
    uh2 = [_sh2(j, x4) - _sh2(j - 1, x4) for j in range(1, n2 + 1)]
    return uh1, uh2


def run(params, prcp, pet, s0=0.5, r0=0.5, full=False):
    """Run GR4J. prcp, pet: daily arrays in mm/day. s0, r0: initial stores as fractions of x1, x3.

    Returns simulated flow Q (mm/day). With full=True returns a dict with every store and flux
    (needed by the intervention modules and by the water-balance test):
        q, aet, exchange (actual water gained (+) or lost (-) through x2), s (production store, end of day),
        r (routing store, end of day), uh_store (water still inside the unit hydrographs, end of day),
        perc, pr (effective rainfall sent to routing), qr (routing outflow), qd (direct outflow).
    """
    x1, x2, x3, x4 = params
    P = np.asarray(prcp, dtype=float).tolist()
    E = np.asarray(pet, dtype=float).tolist()
    n = len(P)
    uh1, uh2 = unit_hydrographs(x4)
    n1, n2 = len(uh1), len(uh2)
    q1buf = [0.0] * n1                     # q1buf[k] = UH1 water that will leave in k days' time
    q2buf = [0.0] * n2
    S, R = s0 * x1, r0 * x3
    Q = [0.0] * n
    if full:
        out = {k: [0.0] * n for k in ("aet", "exchange", "s", "r", "uh_store", "perc", "pr", "qr", "qd")}

    for t in range(n):
        p, e = P[t], E[t]
        # interception: rainfall first meets the evaporative demand
        if p >= e:
            pn, en = p - e, 0.0
            tw = math.tanh(min(pn / x1, 13.0))
            ps = x1 * (1 - (S / x1) ** 2) * tw / (1 + S / x1 * tw)
            es = 0.0
        else:
            pn, en = 0.0, e - p
            tw = math.tanh(min(en / x1, 13.0))
            es = S * (2 - S / x1) * tw / (1 + (1 - S / x1) * tw)
            ps = 0.0
        S = S - es + ps
        perc = S * (1 - (1 + (4.0 / 9.0 * S / x1) ** 4) ** -0.25)
        S -= perc
        pr = perc + (pn - ps)

        # split 90/10 between the two unit hydrographs, then shift the buffers by one day
        for k in range(n1):
            q1buf[k] += 0.9 * pr * uh1[k]
        for k in range(n2):
            q2buf[k] += 0.1 * pr * uh2[k]
        q9, q1 = q1buf[0], q2buf[0]
        q1buf = q1buf[1:] + [0.0]
        q2buf = q2buf[1:] + [0.0]

        f = x2 * (R / x3) ** 3.5           # groundwater exchange
        r_new = R + q9 + f
        f_r = f if r_new >= 0 else -(R + q9)   # actual exchange on the routing branch
        R = max(0.0, r_new)
        qr = R * (1 - (1 + (R / x3) ** 4) ** -0.25)
        R -= qr
        qd_raw = q1 + f
        f_d = f if qd_raw >= 0 else -q1        # actual exchange on the direct branch
        qd = max(0.0, qd_raw)
        Q[t] = qr + qd

        if full:
            out["aet"][t] = es + min(p, e)
            out["exchange"][t] = f_r + f_d
            out["s"][t], out["r"][t] = S, R
            out["uh_store"][t] = sum(q1buf) + sum(q2buf)
            out["perc"][t], out["pr"][t], out["qr"][t], out["qd"][t] = perc, pr, qr, qd

    if not full:
        return np.array(Q)
    out = {k: np.array(v) for k, v in out.items()}
    out["q"] = np.array(Q)
    out["s0"], out["r0"] = s0 * x1, r0 * x3
    return out


def water_balance_error(out, prcp):
    """P - AET - Q + exchange - (change in all stores), mm over the whole run. Should be ~0."""
    storage_end = out["s"][-1] + out["r"][-1] + out["uh_store"][-1]
    storage_start = out["s0"] + out["r0"]
    return (np.sum(prcp) - out["aet"].sum() - out["q"].sum() + out["exchange"].sum()
            - (storage_end - storage_start))
