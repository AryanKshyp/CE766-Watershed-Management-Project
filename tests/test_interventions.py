import numpy as np
import pytest

from src import gr4j
from src.interventions import Bucket, Portfolio, Works, reservoir, zhang_et
from tests.test_gr4j import PARAMS, synthetic_forcing


@pytest.mark.parametrize('portfolio', [Portfolio(), Portfolio(1), Portfolio(bunds=1),
                                       Portfolio(checks=1), Portfolio(forest=1), Portfolio(1, 1, 1, 1)])
def test_catchment_with_works_closes(portfolio):
    rain, pet = synthetic_forcing(730)
    factor = zhang_et(rain.mean(), pet.mean(), .31 + .01 * portfolio.forest) / zhang_et(
        rain.mean(), pet.mean(), .31)
    works = Works(portfolio, pet, np.full(len(pet), 1 / 151), 2.0)
    out = gr4j.run(PARAMS, rain, pet * factor, full=True, works=works)
    assert abs(gr4j.water_balance_error(out, rain) - works.external_water_mm()) < 1e-8
    if portfolio == Portfolio():
        np.testing.assert_array_equal(out['q'], gr4j.run(PARAMS, rain, pet))


def test_bucket_fills_spills_and_empties():
    b = Bucket(1, 210, 100)
    spill, evap, seep, take = b.step(2 * b.capacity, 0, 0, 0)
    assert (spill, evap, seep, take) == (b.capacity, 0, 0, 0)
    spill, evap, seep, take = b.step(0, 2, 3, 1)
    assert b.storage == 0
    assert abs(evap + seep + take - b.capacity) < 1e-12


def test_reservoir_daily_balance_and_shortage():
    inflow = np.array([100., 0., 0., 0.])
    r = reservoir(inflow, np.ones(4), 4., 7., 1.)
    delta = np.diff(r['storage'], prepend=r['initial'])
    np.testing.assert_allclose(delta, inflow - r['supply'] - r['evap'] - r['river'], atol=1e-12)
    assert r['storage'][0] == 7 and r['river'][0] > 1 and r['supply'][-1] == 0
