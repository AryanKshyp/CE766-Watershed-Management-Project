"""Reproduce the final tables and two upload figures: python -m src.final_analysis."""
from itertools import product

import numpy as np
import pandas as pd

from src import PROCESSED, ROOT, gr4j, planning
from src.interventions import (CHANDIL_AREA, DEMAND_MCM_DAY, FOREST_HA, LIVE_MCM,
                               Portfolio, Works, reservoir, zhang_et)

TABLE = ROOT / 'outputs' / 'tables'
AREA, KHARKAI = 12785., 6350.2


def study_years(d):
    # 1980 warms up storage. Both endpoints below enclose whole June-May years.
    whole = d.loc['1981-06-01':'2018-05-31']
    wy = planning.water_year(whole.index)
    coverage = whole.q_obs_mm.notna().groupby(wy).mean()
    kept = coverage.index[coverage >= planning.MIN_OBS_FRAC]
    rain = whole[whole.index.month.isin([6, 7, 8, 9])].prcp.groupby(
        lambda date: date.year).sum().loc[kept]
    return kept, rain, rain.index[rain <= rain.quantile(1 / 3)]


def rabi_weights(dates):
    season = ((dates.month >= 10) | (dates.month <= 2)).astype(float)
    wy = planning.water_year(dates)
    # Calendrical season length stays correct even for partial endpoint years.
    leap = pd.to_datetime([f'{y+1}-02-01' for y in np.unique(wy)]).days_in_month
    length = dict(zip(np.unique(wy), 123 + leap))
    return season / np.array([length[y] for y in wy])


def main():
    sim = pd.read_parquet(PROCESSED / 'gr4j_sim.parquet')
    d = sim[sim.gauge_id == '06008'].set_index('date').sort_index()
    kh = sim[sim.gauge_id == '06001'].set_index('date').loc[d.index]
    params = pd.read_csv(TABLE / 'gr4j_params.csv', dtype={'gauge_id': str}).set_index('gauge_id')
    attrs = pd.read_parquet(PROCESSED / 'study_attributes.parquet').set_index('gauge_id')
    forest = attrs.loc['06008', 'trees_frac']
    x = params.loc['06008', ['x1', 'x2', 'x3', 'x4']].to_numpy(float)
    kept, rain, dry = study_years(d)
    wy = planning.water_year(d.index)
    keep = np.isin(wy, kept)
    obs = d.q_obs_mm.notna().to_numpy()
    q95 = d.q_obs_mm[keep].quantile(.05) * AREA / 86.4
    yields = pd.DataFrame(index=kept)
    for key, output in [('q_obs_mm', 'observed_mcm'), ('q_sim_mm', 'gr4j_mcm')]:
        yields[output] = planning.annual_yield_mcm(d.index[keep], d[key][keep], AREA, obs[keep])
    yields['rain_mm'] = rain
    yields['deficient'] = yields.index.isin(dry)
    yields.to_csv(TABLE / 'final_water_years.csv', index_label='june_year')
    forcing = pd.read_parquet(PROCESSED / 'study_daily.parquet', columns=['gauge_id','date','aet_gleam'])
    gleam = forcing[forcing.gauge_id == '06008'].set_index('date').loc[d.index, 'aet_gleam']
    matched = keep & obs
    p, e = d.prcp[matched].mean() * 365, d.pet[matched].mean() * 365
    theory = {'p_mm_year': p, 'pet_mm_year': e, 'p_minus_q': p - 365*d.q_obs_mm[matched].mean(),
              'zhang_et': zhang_et(p, e, forest), 'gr4j_et': 365*d.aet_sim[matched].mean(),
              'gleam_et': 365*gleam[matched].mean(), 'q95_m3s': q95}
    dry_obs = d.q_obs_mm[np.isin(wy, dry) & (d.index.month <= 5)].dropna() * AREA / 86.4
    theory['deficient_jan_may_observed_days'] = len(dry_obs)
    theory['deficient_jan_may_observed_eflow_pct'] = 100 * (dry_obs >= q95).mean()
    pd.DataFrame([theory]).to_csv(TABLE / 'final_theory.csv', index=False)
    jan_may = d.index.month <= 5
    both = jan_may & d.q_obs_mm.notna() & kh.q_obs_mm.notna() & (d.index.year >= 1981)
    paired = pd.DataFrame({'outlet': d.q_obs_mm*AREA/86.4, 'kharkai': kh.q_obs_mm*KHARKAI/86.4})[both]
    paired['increment'] = paired.outlet - paired.kharkai
    regulation = paired.groupby(paired.index.year).mean()
    regulation['paired_days'] = paired.groupby(paired.index.year).size()
    regulation[regulation.paired_days >= 0.8 * 151].to_csv(TABLE / 'final_regulation.csv', index_label='year')

    rows = []
    weights = rabi_weights(d.index)
    base_pet = d.pet.to_numpy()
    for scenario, pet_factor, seep, need, demand_factor, capacity_factor, release_factor in [
            ('Reference', 1., 2., 375., 1., 1., 1.),
            ('Stress', 1.10, 5., 450., 1.25, .50, .50)]:
        ep = base_pet * pet_factor
        demand = DEMAND_MCM_DAY * demand_factor
        # Untreated tributary and small intervening area bypass Chandil.
        kx = params.loc['06001', ['x1', 'x2', 'x3', 'x4']].to_numpy(float)
        kh_q = gr4j.run(kx, kh.prcp, kh.pet * pet_factor)
        local_q = gr4j.run(x, d.prcp, ep)
        bypass = (kh_q * KHARKAI + local_q * (AREA - KHARKAI - CHANDIL_AREA)) / 1000
        for switches in product((0, 1), repeat=4):
            plan = Portfolio(*switches)
            f = forest + plan.forest * FOREST_HA / (100 * CHANDIL_AREA)
            ratio = zhang_et(p, e*pet_factor, f) / zhang_et(p, e*pet_factor, forest)
            works = Works(plan, ep, weights, seep)
            out = gr4j.run(x, d.prcp, ep * ratio, works=works, full=True)
            residual = gr4j.water_balance_error(out, d.prcp) - works.external_water_mm()
            if abs(residual) > 1e-6:
                raise ValueError(f'Catchment balance failed for {plan.name()}: {residual}')
            inflow = out['q'] * CHANDIL_AREA / 1000
            river_target = q95 * .0864 * CHANDIL_AREA / AREA * release_factor
            dam = reservoir(inflow, ep, demand, LIVE_MCM * capacity_factor, river_target)
            delta = np.diff(dam['storage'], prepend=dam['initial'])
            np.testing.assert_allclose(inflow - dam['supply'] - dam['river'] - dam['evap'], delta, atol=1e-10)
            downstream = (dam['river'] + bypass) / .0864
            irrigated = pd.Series(works.withdrawal * CHANDIL_AREA * 100 / need).groupby(wy).sum()
            for period, years in [('All', kept), ('Deficient', dry)]:
                selected = np.isin(wy, years)
                winter = selected & jan_may
                rows.append(dict(scenario=scenario, portfolio=plan.name(), period=period,
                                 n_years=len(years), rabi_ha=irrigated.loc[years].mean(),
                                 supply_pct=100*np.mean(dam['supply'][selected] >= demand - 1e-10),
                                 eflow_pct=100*np.mean(downstream[winter] >= q95),
                                 cost_crore=plan.cost_crore(), cost_low=.7*plan.cost_crore(),
                                 cost_high=1.3*plan.cost_crore()))
    table = pd.DataFrame(rows)
    table.to_csv(TABLE / 'final_portfolios.csv', index=False)
    from src.final_figures import draw
    draw(yields, table)


if __name__ == '__main__':
    main()
