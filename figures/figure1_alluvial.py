"""Figure 1. Path through the prespecified three-item composite.

Alluvial diagram of the 332 models through validation strategy, leakage safeguard and
calibration assessment to status on the three-item composite. Ribbons are coloured by
composite status: all three components met; validation beyond the development sample and
a leakage safeguard but no calibration assessment; validation or leakage safeguard not met.

    python figures/figure1_alluvial.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle

import common as C

df = C.load()
N = len(df)

df['v'] = df.validation
df['l'] = np.where(df.item_leakage == 1, 'Present', 'Unclear')
df['c'] = np.where(df.item_calibration == 1, 'Assessed', 'Not assessed')
df['k'] = np.select([df.composite == 1,
                     (df.item_validation == 1) & (df.item_leakage == 1) & (df.item_calibration == 0)],
                    ['met', 'near'], 'other')

AXES = [  # (header, column, strata from top to bottom)
    ('Validation', 'v', ['External', 'Temporal', 'Internal only']),
    ('Leakage\nsafeguard', 'l', ['Present', 'Unclear']),
    ('Calibration', 'c', ['Assessed', 'Not assessed']),
    ('Three-item\ncomposite', 'k', ['met', 'near', 'other']),
]
RANK = {col: {s: i for i, s in enumerate(strata)} for _, col, strata in AXES}
COLOR = {'met': C.BLUE_DEEP, 'near': C.BLUE_LIGHT, 'other': '#d3d2cb'}
SORT = {'v': 'vklc', 'l': 'lkvc', 'c': 'cklv', 'k': 'kclv'}   # within-stratum ordering

alluvia = df.groupby(['v', 'l', 'c', 'k']).size().reset_index(name='n')

# layout in inches
FW, FH = 6.38, 3.42
fig = plt.figure(figsize=(FW, FH))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis('off')

Y_TOP, Y_BOT = FH - 0.74, 0.48
GAP = 0.06
SCALE = (Y_TOP - Y_BOT - 2 * GAP) / N
X = [0.76, 2.13, 3.51, 4.88]
W = [0.022, 0.022, 0.022, 0.0]


def spans(col, strata):
    counts = df[col].value_counts()
    gap = GAP if len(strata) == 3 else 2 * GAP
    out, y = {}, Y_TOP
    for s in strata:
        h = counts.get(s, 0) * SCALE
        out[s] = (y, y - h)
        y -= h + gap
    return out


SPANS = [spans(col, strata) for _, col, strata in AXES]
POS = {}
for j, (_, col, strata) in enumerate(AXES):
    keyed = alluvia.assign(**{f'_{c}': alluvia[c].map(RANK[c]) for c in 'vlck'})
    order = keyed.sort_values([f'_{c}' for c in SORT[col]])
    cursor = {s: SPANS[j][s][0] for s in strata}
    for i, row in order.iterrows():
        top = cursor[row[col]]
        POS[(i, j)] = (top, top - row.n * SCALE)
        cursor[row[col]] = top - row.n * SCALE


def ribbon(x0, x1, t0, b0, t1, b1):
    xm = (x0 + x1) / 2
    verts = [(x0, t0), (xm, t0), (xm, t1), (x1, t1), (x1, b1), (xm, b1), (xm, b0), (x0, b0), (x0, t0)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    return Path(verts, codes)


for z, k in enumerate(['other', 'near', 'met']):
    for i, row in alluvia[alluvia.k == k].iterrows():
        for j in range(3):
            t0, b0 = POS[(i, j)]
            t1, b1 = POS[(i, j + 1)]
            p = ribbon(X[j] + W[j] / 2, X[j + 1] - W[j + 1] / 2, t0, b0, t1, b1)
            ax.add_patch(PathPatch(p, facecolor=COLOR[k], edgecolor='none', alpha=0.85, zorder=2 + z))

for j in range(3):
    for s, (top, bot) in SPANS[j].items():
        ax.add_patch(Rectangle((X[j] - W[j] / 2, bot), W[j], top - bot, facecolor='#2b2a27',
                               edgecolor='none', zorder=10))


def pct(n):
    return f'{n} ({100 * n / N:.1f}%)'


def label(x, y, text, ha='center', va='center', bold=False, color=C.INK):
    ax.text(x, y, text, ha=ha, va=va, fontsize=8.2 if bold else 8.0, color=color,
            fontweight='bold' if bold else 'normal', linespacing=1.0)


for j, (head, _, _) in enumerate(AXES):
    ax.text(X[j], FH - 0.13, head, ha='center', va='top', fontsize=8.8, fontweight='bold',
            color=C.INK, linespacing=1.0)

cv = df.v.value_counts()
for s in AXES[0][2]:
    top, bot = SPANS[0][s]
    label(X[0] - 0.06, (top + bot) / 2, f'{s}\n{pct(cv[s])}', ha='right')

for j in (1, 2):
    _, col, strata = AXES[j]
    cnt = df[col].value_counts()
    label(X[j], Y_TOP + 0.04, f'{strata[0]}\n{pct(cnt[strata[0]])}', va='bottom')
    label(X[j], Y_BOT - 0.04, f'{strata[1]}\n{pct(cnt[strata[1]])}', va='top')

ck = df.k.value_counts()
met_top, met_bot = SPANS[3]['met']
label(X[3] + 0.04, (met_top + met_bot) / 2, f'Met all three\n{pct(ck["met"])}', ha='left',
      bold=True, color=C.BLUE_DEEP)
near_top = SPANS[3]['near'][0]
other_bot = SPANS[3]['other'][1]
BX = X[3] + 0.11
ax.plot([BX - 0.04, BX, BX, BX - 0.04], [near_top, near_top, other_bot, other_bot],
        color=C.INK, lw=0.7, zorder=11)
label(BX + 0.07, near_top + 0.01, f'Did not meet all three\n{pct(int((df.k != "met").sum()))}',
      ha='left', va='top', bold=True)
for s, text in [('near', 'Missed only calibration'),
                ('other', 'Missed validation or\nleakage safeguard')]:
    top, bot = SPANS[3][s]
    label(BX + 0.15, (top + bot) / 2 - (0.12 if s == 'near' else 0), f'{text}\n{pct(ck[s])}', ha='left')

C.save(fig, 'figure1_alluvial')
