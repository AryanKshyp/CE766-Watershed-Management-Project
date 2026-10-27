"""Read raw CAMELS-IND v2.2 files into tidy pandas dataframes.

Raw layout and quirks are documented in docs/data_notes.md. Nothing here writes to data/raw.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "camels_ind"
PROCESSED = ROOT / "data" / "processed"

EASTERN_BASINS = ["Subernarekha", "Brahmani-Baitarani", "Mahanadi"]
ATTRIBUTE_GROUPS = ["name", "topo", "clim", "hydro", "land", "soil", "geol", "anth"]

# Dates where the raw temperature grid has zeros (found by scanning all 242 forcing files; see data_notes.md)
BAD_TEMPERATURE_DATES = {"tmin": ["2019-01-11", "2019-05-08"], "tmax": ["2019-05-07"]}

# Attributes computed from observed streamflow. Allowed for interpreting results, NEVER as model inputs
# (an ungauged catchment would not have them). reservoir_index = storage / observed annual flow.
STREAMFLOW_DERIVED = ["flow_availability", "reservoir_index", "dor"]  # plus every column of camels_ind_hydro


def streamflow_derived_columns():
    """Every attribute that is computed from observed streamflow (rule 2: never a model input)."""
    hydro = pd.read_csv(RAW / "attributes_csv" / "camels_ind_hydro.csv", nrows=0).columns.drop("gauge_id")
    return list(hydro) + STREAMFLOW_DERIVED


def gauge_str(x):
    """CAMELS-IND gauge IDs are 5 digits (2-digit CWC basin code + station no.); some files drop the leading 0."""
    return f"{int(float(x)):05d}"


def read_attributes(groups=ATTRIBUTE_GROUPS):
    """All static attributes merged into one table indexed by gauge_id (string, e.g. '07001')."""
    frames = []
    for g in groups:
        d = pd.read_csv(RAW / "attributes_csv" / f"camels_ind_{g}.csv")
        d["gauge_id"] = d["gauge_id"].map(gauge_str)
        frames.append(d.set_index("gauge_id"))
    return pd.concat(frames, axis=1)


def read_streamflow(kind="observed"):
    """Daily streamflow in m3/s, wide: rows = dates, columns = gauge_id. kind = 'observed' or 'lstm'.

    Missing observed days are NaN in the raw file and are left as NaN (never gap-filled).
    """
    fname = {"observed": "streamflow_observed.csv", "lstm": "lstm_pred_streamflow.csv"}[kind]
    d = pd.read_csv(RAW / "streamflow_timeseries" / fname)
    d.index = pd.to_datetime(d[["year", "month", "day"]])
    d.index.name = "date"
    d = d.drop(columns=["year", "month", "day"])
    d.columns = [gauge_str(c) for c in d.columns]
    return d


def read_forcings(gauge_id):
    """Daily catchment-mean forcings for one gauge, indexed by date, with units stripped from column names.

    Fixes one known artefact: on three dates in 2019 the temperature grid contains zeros (a missing-value
    code), so catchment means are exactly 0 degC or pulled far too low (e.g. tmax 5 degC in May in Odisha).
    Those values are set to NaN on every catchment, filled by linear interpolation from the neighbouring
    days, and tavg is recomputed as (tmax + tmin) / 2.
    """
    d = pd.read_csv(RAW / "catchment_mean_forcings" / f"{gauge_str(gauge_id)}.csv")
    d.index = pd.to_datetime(d[["year", "month", "day"]])
    d.index.name = "date"
    d = d.drop(columns=["year", "month", "day"])
    d.columns = [c.split("(")[0] for c in d.columns]
    for c, dates in BAD_TEMPERATURE_DATES.items():
        d.loc[pd.to_datetime(dates), c] = np.nan
        d[c] = d[c].interpolate(limit=3)
    d["tavg"] = (d["tmax"] + d["tmin"]) / 2
    return d


def m3s_to_mm_day(q_m3s, area_km2):
    """Convert discharge (m3/s) to catchment depth (mm/day)."""
    return q_m3s * 86.4 / area_km2


def read_gauge_points():
    """Gauge outlet locations (CWC lat/lon) from the topo attributes, with basin and name."""
    a = read_attributes(["name", "topo"])
    return a[["cwc_site_name", "river_basin", "cwc_river", "cwc_lat", "cwc_lon"]]
