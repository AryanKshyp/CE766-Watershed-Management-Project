import numpy as np

from src import gr4j

PARAMS = [350.0, -1.0, 90.0, 2.4]


def synthetic_forcing(n=3 * 365, seed=42):
    rng = np.random.default_rng(seed)
    doy = np.arange(n) % 365
    monsoon = (doy > 150) & (doy < 270)
    prcp = np.where(rng.random(n) < np.where(monsoon, 0.6, 0.05), rng.gamma(0.8, 18, n), 0.0)
    pet = 3 + 2 * np.sin(2 * np.pi * (doy - 80) / 365)
    return prcp, pet


def test_unit_hydrographs_sum_to_one():
    for x4 in [0.6, 1.0, 2.4, 5.7]:
        uh1, uh2 = gr4j.unit_hydrographs(x4)
        assert abs(sum(uh1) - 1) < 1e-12 and abs(sum(uh2) - 1) < 1e-12


def test_water_balance_closes():
    prcp, pet = synthetic_forcing()
    for params in [PARAMS, [800.0, 2.0, 300.0, 1.2], [100.0, -5.0, 20.0, 4.0]]:
        out = gr4j.run(params, prcp, pet, full=True)
        assert abs(gr4j.water_balance_error(out, prcp)) < 1e-6


def test_zero_rain_gives_monotonic_recession():
    n = 200
    q = gr4j.run(PARAMS, np.zeros(n), np.full(n, 3.0), s0=0.8, r0=0.8)
    assert np.all(np.diff(q[5:]) <= 1e-12)     # after the unit hydrographs have emptied


def test_flow_never_negative():
    prcp, pet = synthetic_forcing()
    for x2 in [-8.0, 0.0, 6.0]:
        q = gr4j.run([300.0, x2, 50.0, 2.0], prcp, pet)
        assert np.all(q >= 0)
