"""Figures for the Subarnarekha study.

Run from the project root (after python -m src.calibrate):  python -m src.figures
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import planning
from src.load import PROCESSED, RAW, ROOT
from src.metrics import all_metrics

FIG = ROOT / "outputs" / "figures"
OBS, SIM, ACCENT = "#0b0b0b", "#2a78d6", "#eb6834"      # ink, blue, orange (validated CVD-safe pair)
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
AREA = {"06008": 12785.0, "06001": 6350.2}

# Approximate locations (deg E, deg N), placed by hand for orientation only
PLACES = {"Bokaro": (86.15, 23.67), "Ranchi": (85.33, 23.36), "Jamshedpur": (86.20, 22.80)}
DAMS = {"Getalsud dam": (85.54, 23.46), "Chandil dam": (86.02, 22.97)}

plt.rcParams.update({
    "font.size": 8.5, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.axisbelow": True,
    "legend.frameon": False, "savefig.dpi": 300, "savefig.bbox": "tight",
})


def panel_map(ax):
    cat = gpd.read_file(RAW / "shapefiles_catchment" / "catchments.shp")
    cat.plot(ax=ax, color="#f0efec", edgecolor="#d6d5cf", linewidth=0.4)
    cat[cat.gauge_id == "06008"].plot(ax=ax, color=SIM, alpha=0.18, edgecolor=SIM, linewidth=0.9)
    cat[cat.gauge_id == "06001"].plot(ax=ax, color=SIM, alpha=0.22, edgecolor="white", linewidth=0.8)
    pts = pd.read_csv(RAW / "attributes_csv" / "camels_ind_topo.csv")
    pts["gauge_id"] = pts.gauge_id.map(lambda x: f"{int(float(x)):05d}")
    for g, label, off in [("06008", "Jamshedpur gauge", (5, -9)), ("06001", "Adityapur gauge\n(Kharkai)", (-62, -14))]:
        r = pts[pts.gauge_id == g].iloc[0]
        ax.scatter(r.cwc_lon, r.cwc_lat, s=30, marker="s", color=SIM, edgecolor="white", linewidth=0.8, zorder=4)
        ax.annotate(label, (r.cwc_lon, r.cwc_lat), xytext=off, textcoords="offset points", fontsize=7, color=INK)
    for name, (x, y) in DAMS.items():
        ax.scatter(x, y, s=42, marker="^", color=ACCENT, edgecolor="white", linewidth=0.8, zorder=4)
        ax.annotate(name, (x, y), xytext=(5, 3), textcoords="offset points", fontsize=7, color=INK)
    ax.scatter(*PLACES["Bokaro"], s=110, marker="*", color=INK, zorder=4)
    ax.annotate("Bokaro (home;\nDamodar basin)", PLACES["Bokaro"], xytext=(6, -2), textcoords="offset points", fontsize=7, color=INK)
    ax.scatter(*PLACES["Ranchi"], s=14, color=INK, zorder=4)
    ax.annotate("Ranchi", PLACES["Ranchi"], xytext=(-8, 5), textcoords="offset points", fontsize=7, color=INK)
    ax.text(85.55, 22.55, "Kharkai", fontsize=7, color=MUTED, style="italic")
    ax.text(85.55, 23.20, "upper Subarnarekha", fontsize=7, color=MUTED, style="italic")
    ax.set_xlim(84.9, 86.9); ax.set_ylim(21.9, 23.95); ax.set_aspect("equal"); ax.grid(False)
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
    ax.set_title("(a) Study watershed: Subarnarekha above Jamshedpur", loc="left", fontsize=9)


def panel_hydrograph(ax, d):
    w = d[(d.date >= "2011-06-01") & (d.date <= "2011-10-31")]
    f = 12785.0 / 86.4
    ax.plot(w.date, w.q_obs_mm * f, color=OBS, lw=1.2, label="Observed")
    ax.plot(w.date, w.q_sim_mm * f, color=SIM, lw=1.2, label="GR4J")
    val = d[(d.date > "2009-12-31") & (d.date <= "2018-12-31")]
    m = all_metrics(val.q_obs_mm.values, val.q_sim_mm.values)
    ax.text(0.02, 0.95, f"Validation 2010–18: KGE {m['kge']:.2f}, NSE {m['nse']:.2f}", transform=ax.transAxes,
            fontsize=7.5, va="top", color=INK)
    ax.set_ylabel("Daily flow (m³/s)")
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b"))
    ax.legend(loc="upper right", fontsize=7.5)
    ax.set_title("(b) Jamshedpur, monsoon 2011 (validation period)", loc="left", fontsize=9)


def panel_dependable(ax, d):
    d = d[d.date <= "2017-05-31"]
    m = d.q_obs_mm.notna().values
    for col, color, label in [("q_obs_mm", OBS, "Observed"), ("q_sim_mm", SIM, "GR4J")]:
        y = planning.annual_yield_mcm(d.date, d[col].values, AREA["06008"], m).sort_values(ascending=False)
        exc = 100 * np.arange(1, len(y) + 1) / (len(y) + 1)
        ax.plot(exc, y.values / 1000, color=color, lw=1.2, marker="o", ms=3.5, label=label)
        dep = y.quantile(0.25) / 1000
        ax.annotate(f"{dep * 1000:,.0f} MCM", (75, dep), xytext=(5, 5) if col == "q_sim_mm" else (-52, -13),
                    textcoords="offset points", fontsize=7, color=INK)
    ax.axvline(75, color=MUTED, lw=0.8, ls="--")
    ax.text(76, 14.8, "75% dependable", fontsize=7, color=MUTED, va="top")
    ax.set_xlabel("Years in which this yield is equalled or exceeded (%)")
    ax.set_ylabel("Water-year yield, Jun–May (1000 MCM)")
    ax.legend(loc="lower left", fontsize=7.5)
    ax.set_title("(c) Dependable yield at Jamshedpur, 36 water years 1980–2016", loc="left", fontsize=9)


def main():
    sim = pd.read_parquet(PROCESSED / "gr4j_sim.parquet")
    d = sim[sim.gauge_id == "06008"]
    fig = plt.figure(figsize=(11, 4.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.15], hspace=0.55, wspace=0.18)
    panel_map(fig.add_subplot(gs[:, 0]))
    panel_hydrograph(fig.add_subplot(gs[0, 1]), d)
    panel_dependable(fig.add_subplot(gs[1, 1]), d)
    fig.savefig(FIG / "fig1_study_area_gr4j_baseline.png")
    print("saved")


if __name__ == "__main__":
    main()
