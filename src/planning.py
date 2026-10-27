"""Planning metrics for the baseline (no-intervention) run: water-year yields, 75% dependable yield,
Q95, mean annual peak, and wet / normal / deficient monsoon classes.

Water year = June to May, labelled by the June year. A year counts only if >= 80% of its days are observed.
"""
import numpy as np
import pandas as pd

MIN_OBS_FRAC = 0.8


def water_year(dates):
    dates = pd.DatetimeIndex(dates)
    return np.where(dates.month >= 6, dates.year, dates.year - 1)


def annual_yield_mcm(dates, q_mm, area_km2, obs_mask):
    """Mean daily flow over observed days x 365, as a volume (1 mm over 1 km2 = 0.001 MCM). Good years only."""
    d = pd.DataFrame({"wy": water_year(dates), "q": np.where(obs_mask, q_mm, np.nan), "ok": obs_mask})
    g = d.groupby("wy")
    good = g.ok.mean() >= MIN_OBS_FRAC
    return (g.q.mean() * 365 * area_km2 / 1000)[good]


def monsoon_class(dates, prcp):
    """Jun-Sep rainfall per water year, split into terciles: deficient / normal / wet."""
    d = pd.DataFrame({"wy": water_year(dates), "p": prcp}, index=pd.DatetimeIndex(dates))
    jjas = d[d.index.month.isin([6, 7, 8, 9])].groupby("wy").p.sum()
    t1, t2 = jjas.quantile([1 / 3, 2 / 3])
    return pd.cut(jjas, [-np.inf, t1, t2, np.inf], labels=["deficient", "normal", "wet"]), jjas


def summary(dates, q_mm, area_km2, obs_mask, prcp):
    """The baseline planning numbers for one flow series (observed or simulated, same days)."""
    y = annual_yield_mcm(dates, q_mm, area_km2, obs_mask)
    cls, _ = monsoon_class(dates, prcp)
    q = pd.Series(np.where(obs_mask, q_mm, np.nan)) * area_km2 / 86.4
    peaks = q.groupby(water_year(dates)).max()[y.index]
    by_cls = y.groupby(cls.reindex(y.index), observed=True).mean()
    return {"mean_yield_mcm": y.mean(), "dependable_75_mcm": y.quantile(0.25),
            "deficient_yield_mcm": by_cls["deficient"], "normal_yield_mcm": by_cls["normal"],
            "wet_yield_mcm": by_cls["wet"], "q95_m3s": q.quantile(0.05), "q50_m3s": q.median(),
            "mean_annual_peak_m3s": peaks.mean(), "n_years": len(y)}
