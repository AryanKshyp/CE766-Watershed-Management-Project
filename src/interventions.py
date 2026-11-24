"""Daily screening model. GR4J uses mm over the Chandil catchment, reservoir uses MCM."""
from dataclasses import dataclass

import numpy as np

CHANDIL_AREA = 5646.0
LIVE_MCM = 1446.966 - 58.622
DEMAND_MCM_DAY = 494 / 365
POND_COUNT, BUND_HA, CHECK_COUNT, FOREST_HA = 1000, 1000, 100, 1000


@dataclass(frozen=True)
class Portfolio:
    ponds: int = 0
    bunds: int = 0
    checks: int = 0
    forest: int = 0

    def name(self):
        names = ('Ponds', 'Bunds', 'Check dams', 'Forest')
        return ' + '.join(n for n, on in zip(names, self.switches()) if on) or 'Baseline'

    def switches(self):
        return self.ponds, self.bunds, self.checks, self.forest

    def cost_crore(self):
        costs = (POND_COUNT * 33000, BUND_HA * (8062985 / 703),
                 CHECK_COUNT * (767237 / 4), FOREST_HA * 92626)
        return sum(on * cost for on, cost in zip(self.switches(), costs)) / 1e7


def zhang_et(p, pet, tree_fraction):
    """Annual screening relationship, using the project's cover-weighted w."""
    aridity = pet / p
    w = 0.5 + 1.5 * tree_fraction
    return p * (1 + w * aridity) / (1 + w * aridity + 1 / aridity)


class Bucket:
    """Pooled structures. State and fluxes are mm over the receiving catchment."""
    def __init__(self, count, volume_m3, surface_m2):
        self.capacity = count * volume_m3 / (1000 * CHANDIL_AREA)
        self.surface_fraction = count * surface_m2 / (1e6 * CHANDIL_AREA)
        self.storage = 0.0

    def step(self, inflow, pet, seep_mm, rabi_share):
        if self.capacity == 0:
            return inflow, 0.0, 0.0, 0.0
        available = self.storage + inflow
        spill = max(0.0, available - self.capacity)
        available -= spill
        area = self.surface_fraction * (available / self.capacity) ** (2 / 3)
        evap = min(available, pet * area)
        seep = min(available - evap, seep_mm * area)
        withdrawal = min(available - evap - seep, self.capacity * rabi_share)
        self.storage = available - evap - seep - withdrawal
        return spill, evap, seep, withdrawal


class Works:
    def __init__(self, portfolio, pet, rabi_share, seep_mm):
        self.pet, self.rabi_share, self.seep_mm = pet, rabi_share, seep_mm
        self.pond = Bucket(POND_COUNT * portfolio.ponds, 210, 100)
        self.check = Bucket(CHECK_COUNT * portfolio.checks, 500, 250)
        self.pond_share = portfolio.ponds * POND_COUNT * 0.01 / CHANDIL_AREA
        self.bund_capture = portfolio.bunds * BUND_HA * 0.01 / CHANDIL_AREA * 0.30
        self.check_share = portfolio.checks * CHECK_COUNT * 0.10 / CHANDIL_AREA
        self.pending_recharge = 0.0
        self.withdrawal = np.zeros(len(pet))
        self.evap = np.zeros(len(pet))

    def upland(self, t, runoff):
        inflow = runoff * self.pond_share
        bund = runoff * self.bund_capture
        spill, evap, seep, take = self.pond.step(inflow, self.pet[t], self.seep_mm,
                                                  self.rabi_share[t])
        self.evap[t], self.withdrawal[t] = evap, take
        return runoff - inflow - bund + spill, bund + seep + self.pending_recharge

    def stream(self, t, streamflow):
        incoming = self.check_share * streamflow
        spill, evap, self.pending_recharge, take = self.check.step(
            incoming, self.pet[t], self.seep_mm, self.rabi_share[t])
        self.evap[t] += evap
        self.withdrawal[t] += take
        return streamflow - incoming + spill

    def external_water_mm(self):
        return (self.evap.sum() + self.withdrawal.sum() + self.pond.storage
                + self.check.storage + self.pending_recharge)


def reservoir(inflow, pet, demand, active_capacity, river_target):
    """City allocation first, fixed river release second. Spill passes downstream."""
    start = 0.5 * active_capacity
    storage = start
    result = {k: np.zeros(len(inflow)) for k in ('supply', 'river', 'evap', 'storage')}
    for i, (flow, e) in enumerate(zip(inflow, pet)):
        area = 173.4664 * ((storage + 58.622) / 1446.966) ** (2 / 3)
        available = storage + flow
        evap = min(available, e * area / 1000)
        available -= evap
        supply = min(demand, available)
        available -= supply
        release = min(river_target, available)
        available -= release
        spill = max(0.0, available - active_capacity)
        storage = available - spill
        result['supply'][i], result['river'][i] = supply, release + spill
        result['evap'][i], result['storage'][i] = evap, storage
    result['initial'] = start
    return result
