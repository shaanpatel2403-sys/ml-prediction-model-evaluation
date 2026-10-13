"""Figure 2. Methodological and reporting features of the included models.

A: proportion of the 332 models meeting each appraisal item, grouped into the three
   components of the prespecified composite, the four other items, and the two combined
   criteria, with Wilson 95% confidence intervals.
B: distribution of the seven-item score, with models meeting all three composite
   components shaded separately.

    python figures/figure2_appraisal_items.py
"""
import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import common as C

df = C.load()
N = len(df)


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


LABEL = {
    'item_validation': 'Validation beyond the\ndevelopment sample',
    'item_calibration': 'Calibration assessed',
    'item_leakage': 'Leakage safeguard',
    'item_outcome': 'Outcome defined',
    'item_decision_analysis': 'Decision-analytic evaluation',
    'item_sample_size': 'Sample-size justification',
    'item_code_and_data': 'Code and data available',
}
k = {c: int(df[c].sum()) for c in LABEL}
composite = sorted(['item_validation', 'item_calibration', 'item_leakage'], key=lambda c: -k[c])
other = sorted(['item_outcome', 'item_decision_analysis', 'item_sample_size', 'item_code_and_data'],
               key=lambda c: -k[c])

FW, FH = 7.44, 4.19
fig = plt.figure(figsize=(FW, FH))
A = fig.add_axes([0, 0, 1, 1])
A.set_xlim(0, FW)
A.set_ylim(0, FH)
A.axis('off')


def top(y):            # distance from the top edge, in inches
    return FH - y


# ------------------------------------------------------------------ panel A
LBL_X, BAR_X0, BAR_LEN, VAL_X = 2.54, 2.64, 1.62, 4.34
BAR_H = 0.13
A.text(0.18, top(0.28), 'A', fontsize=11, fontweight='bold', color=C.INK, va='center')
A.text(0.42, top(0.28), f'Models meeting each appraisal item (N = {N})', fontsize=9.5,
       fontweight='bold', color=C.INK, va='center')

rows = [('header', 'Prespecified composite components', 0.58)]
rows += [('item', c, y) for c, y in zip(composite, (0.81, 1.106, 1.40))]
rows += [('rule', None, 1.506), ('header', 'Other appraisal items', 1.62)]
rows += [('item', c, y) for c, y in zip(other, (1.86, 2.09, 2.32, 2.56))]
rows += [('rule', None, 2.66), ('header', 'Combined criteria', 2.78),
         ('combined', 'All three composite components', 3.01),
         ('combined', 'All seven items', 3.25)]


def bar(y, count, color, bold=False):
    yc = top(y)
    A.add_patch(Rectangle((BAR_X0, yc - BAR_H / 2), BAR_LEN, BAR_H, facecolor=C.TRACK,
                          edgecolor='none', zorder=1))
    A.add_patch(Rectangle((BAR_X0, yc - BAR_H / 2), BAR_LEN * count / N, BAR_H, facecolor=color,
                          edgecolor='none', zorder=2))
    if 0 < count < N:   # at 0% and 100% the interval is too narrow to draw
        lo, hi = wilson(count, N)
        xl, xh = BAR_X0 + BAR_LEN * lo, BAR_X0 + BAR_LEN * hi
        A.plot([xl, xh], [yc, yc], color=C.INK, lw=0.9, zorder=3, solid_capstyle='butt')
        for xc in (xl, xh):
            A.plot([xc, xc], [yc - BAR_H * 0.42, yc + BAR_H * 0.42], color=C.INK, lw=0.9, zorder=3)
    share = 100 * count / N
    txt = f'{count} ({share:.0f}%)' if count in (0, N) else f'{count} ({share:.1f}%)'
    A.text(VAL_X, yc, txt, va='center', ha='left', fontsize=8.4, color=C.INK,
           fontweight='bold' if bold else 'normal')


for kind, what, y in rows:
    if kind == 'header':
        A.text(0.42, top(y), what, fontsize=8.2, fontweight='bold', color=C.INK_2, va='center')
    elif kind == 'rule':
        A.plot([0.42, 5.06], [top(y), top(y)], color=C.RULE, lw=0.7)
    elif kind == 'item':
        A.text(LBL_X, top(y), LABEL[what], ha='right', va='center', fontsize=8.4, color=C.INK,
               linespacing=0.95)
        bar(y, k[what], C.BLUE_LIGHT if what in composite else C.GREY)
    else:
        count = int(df.composite.sum()) if what.startswith('All three') else int((df.seven_item_score == 7).sum())
        A.text(LBL_X, top(y), what, ha='right', va='center', fontsize=8.4, color=C.INK,
               fontweight='bold')
        bar(y, count, C.BLUE_DEEP, bold=True)

axis_y = top(3.39)
A.plot([BAR_X0, BAR_X0 + BAR_LEN], [axis_y, axis_y], color=C.RULE, lw=0.7)
for t in (0, 25, 50, 75, 100):
    x = BAR_X0 + BAR_LEN * t / 100
    A.plot([x, x], [axis_y, axis_y - 0.04], color=C.RULE, lw=0.7)
    A.text(x, axis_y - 0.065, f'{t}%', ha='center', va='top', fontsize=7.6, color=C.INK_2)
A.text(BAR_X0 + BAR_LEN / 2, top(3.66), 'Models meeting the item, %', ha='center', va='center',
       fontsize=7.8, color=C.INK_2)

# ------------------------------------------------------------------ panel B
A.text(5.10, top(0.28), 'B', fontsize=11, fontweight='bold', color=C.INK, va='center')
A.text(5.34, top(0.28), 'Seven-item score', fontsize=9.5, fontweight='bold', color=C.INK, va='center')
for (y, color, text) in [(0.73, C.BLUE_DEEP, 'Met all three\ncomposite components'),
                         (0.92, C.GREY, 'Did not meet all three')]:
    A.add_patch(Rectangle((5.53, top(y) - 0.04), 0.10, 0.08, facecolor=color, edgecolor='none'))
    A.text(5.70, top(y), text, fontsize=7.2, color=C.INK, va='center', ha='left', linespacing=0.95)

B_X0, B_X1, B_Y0, B_Y1 = 5.54, 7.24, 0.74, FH - 1.05
B = fig.add_axes([B_X0 / FW, B_Y0 / FH, (B_X1 - B_X0) / FW, (B_Y1 - B_Y0) / FH])
scores = np.arange(8)
tot = np.array([int((df.seven_item_score == s).sum()) for s in scores])
met = np.array([int(((df.seven_item_score == s) & (df.composite == 1)).sum()) for s in scores])
notmet = tot - met
BW = 0.72
B.bar(scores, notmet, width=BW, color=C.GREY, edgecolor='none', zorder=3)
B.bar(scores, met, bottom=notmet, width=BW, color=C.BLUE_DEEP, edgecolor='none', zorder=3)
for s in scores:
    B.text(s, tot[s] + 3.5, str(tot[s]), ha='center', va='bottom', fontsize=7.4, color=C.INK)
    if met[s] >= 12 and notmet[s] > 0:    # label inside the blue segment where it fits
        B.text(s, notmet[s] + met[s] / 2, str(met[s]), ha='center', va='center', fontsize=7.0,
               color=C.WHITE, fontweight='bold', zorder=4)
B.set_xlim(-0.63, 7.6)
B.set_ylim(0, 162)
B.set_xticks(scores)
B.set_yticks([0, 50, 100, 150])
B.tick_params(axis='both', labelsize=7.6, colors=C.INK_2, length=2.5, width=0.6)
B.tick_params(axis='x', length=0)
for side in ('top', 'right'):
    B.spines[side].set_visible(False)
B.spines['left'].set_color(C.RULE)
B.spines['bottom'].set_color(C.RULE)
B.grid(axis='y', color=C.GRID, lw=0.6)
B.set_axisbelow(True)
B.set_xlabel('Items met (of 7)', fontsize=7.8, color=C.INK_2, labelpad=3)
B.set_ylabel('Models, n', fontsize=7.8, color=C.INK_2, labelpad=4)

C.save(fig, 'figure2_appraisal_items')
