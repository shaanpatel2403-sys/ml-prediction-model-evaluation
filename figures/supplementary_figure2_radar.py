"""Supplementary Figure 2. Methodological and reporting profiles by journal.

Percentage of models meeting each of the seven appraisal items in the four journals that
contributed at least 10 models. Axes run clockwise from the most to the least frequently
met item in the full sample.

    python figures/supplementary_figure2_radar.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import common as C

df = C.load()
ITEMS = ['item_outcome', 'item_leakage', 'item_validation', 'item_decision_analysis',
         'item_calibration', 'item_sample_size', 'item_code_and_data']
LABEL = {
    'item_outcome': 'Outcome defined',
    'item_leakage': 'Leakage\nsafeguard',
    'item_validation': 'Validation\nbeyond the\ndevelopment\nsample',
    'item_decision_analysis': 'Decision-analytic\nevaluation',
    'item_calibration': 'Calibration\nassessed',
    'item_sample_size': 'Sample-size\njustification',
    'item_code_and_data': 'Code and data\navailable',
}
assert ITEMS == sorted(ITEMS, key=lambda c: -df[c].mean()), 'axes follow overall frequency'
journals = [j for j in C.JOURNAL_COLOR if (df.journal == j).sum() >= 10]

n = len(ITEMS)
ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
ring = np.concatenate([ang, ang[:1]])

fig = plt.figure(figsize=(8.65, 9.33))
ax = fig.add_axes([0.13, 0.16, 0.74, 0.67], polar=True)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_ylim(0, 100)
ax.grid(False)
ax.spines['polar'].set_visible(False)
ax.set_yticks([])
for lev in (20, 40, 60, 80, 100):
    ax.plot(ring, [lev] * len(ring), color='#d4d4d4', lw=0.9, zorder=0)
    a = np.radians(283)
    ax.text(a, lev, f'{lev}%' if lev == 100 else str(lev), fontsize=9.5, color='#6f6e69',
            ha='center', va='bottom')
for a in ang:
    ax.plot([a, a], [0, 100], color='#d4d4d4', lw=0.9, zorder=0)

for j in journals:
    sub = df[df.journal == j]
    vals = [100 * sub[c].mean() for c in ITEMS]
    v = vals + vals[:1]
    ax.plot(ring, v, color=C.JOURNAL_COLOR[j], lw=2.6, zorder=3)
    ax.fill(ring, v, color=C.JOURNAL_COLOR[j], alpha=0.07, zorder=2)

ax.set_xticks(ang)
ax.set_xticklabels([LABEL[c] for c in ITEMS], fontsize=12, color=C.INK, linespacing=1.1)
ax.tick_params(axis='x', pad=16)

fig.text(0.5, 0.965, 'Methodological and reporting profiles by journal', ha='center', va='center',
         fontsize=15, fontweight='bold', color=C.INK)
fig.text(0.5, 0.935, 'Percentage of models meeting each criterion', ha='center', va='center',
         fontsize=12.5, color=C.INK_2)

# legend: italic journal name, upright model count
fig.canvas.draw()
r = fig.canvas.get_renderer()
for k, j in enumerate(journals):
    col, row = k // 2, k % 2
    x0 = 0.15 + 0.37 * col
    y0 = 0.070 - 0.032 * row
    fig.add_artist(Line2D([x0, x0 + 0.04], [y0, y0], color=C.JOURNAL_COLOR[j], lw=3.2))
    t = fig.text(x0 + 0.052, y0, j, fontsize=11.5, style='italic', color=C.INK, va='center')
    w = t.get_window_extent(r).width / fig.bbox.width
    fig.text(x0 + 0.052 + w, y0, f' (n={int((df.journal == j).sum())})', fontsize=11.5,
             color=C.INK, va='center')

C.save(fig, 'supplementary_figure2_radar')
