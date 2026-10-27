"""Streamflow skill metrics: NSE, KGE (Gupta et al. 2009), PBIAS.

Every function drops pairs where either obs or sim is NaN before computing.
"""
import numpy as np


def _clean(obs, sim):
    obs = np.asarray(obs, dtype=float)
    sim = np.asarray(sim, dtype=float)
    ok = ~(np.isnan(obs) | np.isnan(sim))
    return obs[ok], sim[ok]


def nse(obs, sim):
    """Nash-Sutcliffe efficiency. 1 = perfect, 0 = no better than the observed mean."""
    obs, sim = _clean(obs, sim)
    if len(obs) < 2 or np.var(obs) == 0:
        return np.nan
    return 1 - np.sum((sim - obs) ** 2) / np.sum((obs - obs.mean()) ** 2)


def kge_components(obs, sim):
    """Return (kge, r, alpha, beta). alpha = std ratio, beta = mean ratio (sim/obs)."""
    obs, sim = _clean(obs, sim)
    if len(obs) < 2 or obs.std() == 0 or obs.mean() == 0:
        return np.nan, np.nan, np.nan, np.nan
    r = np.corrcoef(obs, sim)[0, 1] if sim.std() > 0 else 0.0
    alpha = sim.std() / obs.std()
    beta = sim.mean() / obs.mean()
    kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    return kge, r, alpha, beta


def kge(obs, sim):
    """Kling-Gupta efficiency (Gupta et al. 2009). 1 = perfect; > -0.41 beats the mean flow."""
    return kge_components(obs, sim)[0]


def pbias(obs, sim):
    """Percent bias = 100 * sum(sim - obs) / sum(obs). Positive = model overestimates."""
    obs, sim = _clean(obs, sim)
    if len(obs) == 0 or obs.sum() == 0:
        return np.nan
    return 100 * np.sum(sim - obs) / np.sum(obs)


def all_metrics(obs, sim):
    k, r, a, b = kge_components(obs, sim)
    n = len(_clean(obs, sim)[0])
    return {"nse": nse(obs, sim), "kge": k, "r": r, "alpha": a, "beta": b,
            "pbias": pbias(obs, sim), "n_days": n}
