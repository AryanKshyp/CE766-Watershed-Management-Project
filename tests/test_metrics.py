import numpy as np
import pytest

from src.metrics import nse, kge, pbias, kge_components

rng = np.random.default_rng(42)
OBS = rng.gamma(2.0, 2.0, size=500)


def test_perfect_prediction():
    assert nse(OBS, OBS) == pytest.approx(1.0)
    assert kge(OBS, OBS) == pytest.approx(1.0)
    assert pbias(OBS, OBS) == pytest.approx(0.0)


def test_predicting_mean_gives_nse_zero():
    sim = np.full_like(OBS, OBS.mean())
    assert nse(OBS, sim) == pytest.approx(0.0)
    assert pbias(OBS, sim) == pytest.approx(0.0, abs=1e-9)


def test_nan_pairs_are_dropped():
    obs = OBS.copy()
    sim = OBS.copy() * 1.1
    obs[::7] = np.nan
    sim[::5] = np.nan
    ok = ~np.isnan(obs) & ~np.isnan(sim)
    assert nse(obs, sim) == pytest.approx(nse(obs[ok], sim[ok]))
    assert pbias(obs, sim) == pytest.approx(10.0)


def test_kge_components_for_scaled_prediction():
    k, r, alpha, beta = kge_components(OBS, 2 * OBS)
    assert r == pytest.approx(1.0)
    assert alpha == pytest.approx(2.0)
    assert beta == pytest.approx(2.0)
    assert k == pytest.approx(1 - np.sqrt(2))


def test_pbias_sign_positive_when_overestimating():
    assert pbias(OBS, OBS * 1.2) == pytest.approx(20.0)
