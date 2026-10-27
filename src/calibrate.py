"""Calibrate GR4J per gauge on 1981-2009 (1980 = warm-up, not scored) and validate on 2010-2018.

Objective: maximise KGE on observed days (missing days masked, never filled).
Optimiser: scipy differential_evolution, seed 42.

Run from the project root:  python -m src.calibrate
Writes outputs/tables/gr4j_params.csv, gr4j_calval.csv and data/processed/gr4j_sim.parquet.
"""
import time

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from src import gr4j
from src.load import PROCESSED, ROOT
from src.metrics import all_metrics

TABLES = ROOT / "outputs" / "tables"
GAUGES = {"06008": "Jamshedpur (Subarnarekha, incl. Kharkai)", "06001": "Adityapur (Kharkai)"}
WARMUP_END, CAL_END, VAL_END = "1980-12-31", "2009-12-31", "2018-12-31"
# Wide literature ranges (Perrin et al. 2003 report 80% intervals of x1 100-1200, x2 -5..3, x3 20-300, x4 1.1-2.9)
BOUNDS = [(10, 2500), (-10, 6), (10, 800), (0.5, 8)]


def load_gauge(g):
    ts = pd.read_parquet(PROCESSED / "timeseries.parquet", columns=["gauge_id", "date", "prcp", "pet_gleam", "q_obs_mm"])
    d = ts[ts.gauge_id == g].set_index("date").sort_index()
    return d[d.index <= VAL_END]


def calibrate(d):
    cal = (d.index > WARMUP_END) & (d.index <= CAL_END) & d.q_obs_mm.notna().values
    P, E, obs = d.prcp.values, d.pet_gleam.values, d.q_obs_mm.values

    def loss(x):
        q = gr4j.run(x, P, E)
        return -all_metrics(obs[cal], q[cal])["kge"]

    res = differential_evolution(loss, BOUNDS, seed=42, popsize=12, maxiter=80, tol=1e-6, polish=True)
    return res.x, -res.fun


def main():
    params, rows, sims = [], [], []
    for g, name in GAUGES.items():
        d = load_gauge(g)
        t = time.time()
        x, k = calibrate(d)
        print(f"{g} {name}: KGE_cal {k:.3f}  x = {np.round(x, 2)}  ({time.time() - t:.0f} s)")
        out = gr4j.run(x, d.prcp.values, d.pet_gleam.values, full=True)
        wb = gr4j.water_balance_error(out, d.prcp.values)
        params.append({"gauge_id": g, "name": name, "x1": x[0], "x2": x[1], "x3": x[2], "x4": x[3], "water_balance_error_mm": wb})
        for period, lo, hi in [("calibration 1981-2009", WARMUP_END, CAL_END), ("validation 2010-2018", CAL_END, VAL_END)]:
            m = (d.index > lo) & (d.index <= hi)
            rows.append({"gauge_id": g, "period": period, **all_metrics(d.q_obs_mm.values[m], out["q"][m])})
        sims.append(pd.DataFrame({"gauge_id": g, "date": d.index, "prcp": d.prcp.values, "pet": d.pet_gleam.values,
                                  "q_obs_mm": d.q_obs_mm.values, "q_sim_mm": out["q"], "aet_sim": out["aet"],
                                  "exchange_sim": out["exchange"]}))
    pd.DataFrame(params).to_csv(TABLES / "gr4j_params.csv", index=False)
    cv = pd.DataFrame(rows)
    cv.to_csv(TABLES / "gr4j_calval.csv", index=False)
    pd.concat(sims).to_parquet(PROCESSED / "gr4j_sim.parquet", index=False)
    print(cv.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
