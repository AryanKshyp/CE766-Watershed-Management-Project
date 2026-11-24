"""Two standalone submission figures, generated from the final analysis tables."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from src.load import ROOT

OUT = ROOT / 'outputs' / 'final'
TEAL, BLUE, INK, GREY = '#087969', '#27528b', '#183039', '#526773'


def draw(yields, results):
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False,
                         'text.color': INK, 'axes.labelcolor': INK, 'legend.frameon': False})
    fig, ax = plt.subplots(figsize=(9, 5.2))
    fig.subplots_adjust(left=.13, bottom=.18, top=.82, right=.96)
    fig.text(.06, .93, 'Figure 1. How much river water is dependable at Jamshedpur?',
             size=16, weight='bold')
    ax.axvline(75, ls=':', lw=1.4, color=GREY)
    for key, label, colour, off in [('observed_mcm', 'Observed', TEAL, -17),
                                     ('gr4j_mcm', 'GR4J', BLUE, 9)]:
        y = np.sort(yields[key])[::-1]
        exceed = np.linspace(0, 100, len(y))
        ax.plot(exceed, y, label=label, lw=2.4, color=colour,
                ls='-' if key == 'observed_mcm' else '--')
        dep = np.quantile(y, .25)
        ax.scatter(75, dep, color=colour, s=35, zorder=3)
        ax.annotate(f'{dep:,.0f}', (75, dep), xytext=(5, off), textcoords='offset points',
                    color=colour, weight='bold')
    ax.set(xlabel='Share of years equalling or exceeding the yield (%)',
           ylabel='June–May river yield (million m³)', xlim=(0, 100), ylim=(0, None))
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=.19)
    fig.savefig(OUT / 'Figure_1_dependable_yield.png', dpi=220)
    plt.close(fig)

    names = ['Baseline', 'Ponds', 'Bunds', 'Check dams', 'Forest', 'Ponds + Check dams',
             'Ponds + Bunds + Check dams + Forest']
    info = results.query("scenario == 'Reference' and period == 'Deficient'").set_index('portfolio')
    stress = results.query("scenario == 'Stress' and period == 'Deficient'").set_index('portfolio')
    fig, ax = plt.subplots(figsize=(11.8, 5.6))
    ax.axis('off')
    fig.subplots_adjust(left=.035, right=.965, bottom=.12, top=.82)
    fig.text(.035,.94, 'Figure 2. What each investment delivers after a deficient monsoon',
             fontsize=18, weight='bold')
    fig.text(.035,.87, 'Selected portfolios above Chandil  |  Mean additional rabi area and downstream performance',
             fontsize=12, color=GREY)
    fields = ['Investment', 'Rabi area (ha)\nreference', 'Rabi area (ha)\nstress',
              'Supply met\n(% days)¹', 'River ≥ Q95\n(% days)¹', 'Capital cost\n(₹ crore)']
    cells = []
    for n in names:
        row = info.loc[n]
        cells.append(['All four' if n == names[-1] else n,
                      f'{row.rabi_ha:.1f}', f'{stress.loc[n, "rabi_ha"]:.1f}',
                      f'{row.supply_pct:.1f}', f'{row.eflow_pct:.1f}', f'{row.cost_crore:.2f}'])
    table = ax.table(cellText=cells, colLabels=fields, loc='center', cellLoc='center',
                     colWidths=[.23,.16,.15,.15,.16,.15], bbox=[0, .02, 1, .98])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    for (i, j), c in table.get_celld().items():
        c.set_edgecolor('white')
        c.set_facecolor('#dcece8' if i == 6 else ('#f1f4f4' if i % 2 else 'white'))
        if i == 0:
            c.set_facecolor('#254752')
            c.set_text_props(color='white', weight='bold', fontsize=11)
        if j == 0:
            c.set_text_props(ha='left')
    fig.text(.037,.055,'¹ Reference case. Supply uses all days. River flow uses January–May days below the city intake.',
             fontsize=11, color=GREY)
    fig.savefig(OUT / 'Figure_2_portfolios.png', dpi=220)
    plt.close(fig)
