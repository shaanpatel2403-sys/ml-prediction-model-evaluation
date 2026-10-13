"""Figure 3. Co-occurrence of methodological and reporting features.

A: chord diagram of the six appraisal items that vary (outcome definition, met by all 332
   models, is omitted). Ribbon width is proportional to the number of models meeting both
   items; arc length is proportional to an item's total co-occurrence with the others.
B: co-occurrence matrix. Bold values are the number of models meeting both the row and
   column items; percentages are the share of models meeting the row item that also met the
   column item; diagonal values are the total meeting each item.

    python figures/figure3_cooccurrence.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle, Wedge

import common as C

df = C.load()
ITEMS = ['item_validation', 'item_calibration', 'item_leakage', 'item_sample_size',
         'item_code_and_data', 'item_decision_analysis']
LABEL = ['Validation beyond the\ndevelopment sample', 'Calibration\nassessed', 'Leakage\nsafeguard',
         'Sample-size\njustification', 'Code and data\navailable', 'Decision-analytic\nevaluation']
COL = [C.ITEM_COLOR[i] for i in ITEMS]

M = df[ITEMS].to_numpy()
CO = M.T @ M                       # CO[i, j] = models meeting both item i and item j
OFF = CO.copy()
np.fill_diagonal(OFF, 0)
n = len(ITEMS)

FW, FH = 7.44, 4.39
fig = plt.figure(figsize=(FW, FH))
page = fig.add_axes([0, 0, 1, 1])
page.set_xlim(0, FW)
page.set_ylim(0, FH)
page.axis('off')
for x, letter, title in [(0.18, 'A', 'Pairwise co-occurrence'), (3.74, 'B', 'Models meeting both criteria')]:
    page.text(x, FH - 0.28, letter, fontsize=11, fontweight='bold', color=C.INK, va='center')
    page.text(x + 0.24, FH - 0.28, title, fontsize=9.5, fontweight='bold', color=C.INK, va='center')

# ------------------------------------------------------------------ panel A: chord diagram
RING_IN, RING_OUT, R = 0.955, 1.05, 0.925      # ring and ribbon radii (data units)
UNIT = 0.94                                     # inches per data unit
LIM = 1.55
cx, cy = 1.68, FH - 2.26
side = 2 * LIM * UNIT
ax = fig.add_axes([(cx - side / 2) / FW, (cy - side / 2) / FH, side / FW, side / FH])
ax.set_xlim(-LIM, LIM)
ax.set_ylim(-LIM, LIM)
ax.set_aspect('equal')
ax.axis('off')

GAP = 3.0                                       # degrees between arcs
deg = (360 - n * GAP) / OFF.sum()               # degrees per co-occurrence
arcs, a = [], 0.0
for i in range(n):
    span = OFF[i].sum() * deg
    arcs.append((a, a + span))
    a += span + GAP

# sub-arc for each partner: nearest clockwise neighbour first, nearest anticlockwise last,
# so that ribbons between neighbouring arcs do not cross
sub = {}
for i in range(n):
    a0 = arcs[i][0]
    for d in range(n - 1, 0, -1):
        j = (i + d) % n
        w = OFF[i, j] * deg
        sub[(i, j)] = (a0, a0 + w)
        a0 += w


def arc_points(t1, t2, r):
    p = Path.arc(t1, t2)
    return p.vertices * r, p.codes


def ribbon(i, j):
    s0, s1 = sub[(i, j)]
    t0, t1 = sub[(j, i)]
    verts, codes = [], []
    v, c = arc_points(s0, s1, R)
    verts += list(v)
    codes += list(c)
    verts += [(0, 0), (R * np.cos(np.radians(t0)), R * np.sin(np.radians(t0)))]
    codes += [Path.CURVE3, Path.CURVE3]
    v, c = arc_points(t0, t1, R)
    verts += list(v[1:])
    codes += list(c[1:])
    verts += [(0, 0), (R * np.cos(np.radians(s0)), R * np.sin(np.radians(s0))), (0, 0)]
    codes += [Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    return Path(verts, codes)


# gradient fill from item i's colour to item j's colour, clipped to the ribbon
g = np.linspace(-R, R, 400)
GX, GY = np.meshgrid(g, g)
pairs = sorted([(i, j) for i in range(n) for j in range(i + 1, n) if OFF[i, j] > 0],
               key=lambda p: -OFF[p])           # largest first so small ribbons stay visible
for i, j in pairs:
    mi = np.radians(np.mean(sub[(i, j)]))
    mj = np.radians(np.mean(sub[(j, i)]))
    p0 = np.array([R * np.cos(mi), R * np.sin(mi)])
    p1 = np.array([R * np.cos(mj), R * np.sin(mj)])
    dvec = p1 - p0
    t = np.clip(((GX - p0[0]) * dvec[0] + (GY - p0[1]) * dvec[1]) / (dvec @ dvec), 0, 1)[..., None]
    rgba = np.concatenate([(1 - t) * to_rgb(COL[i]) + t * to_rgb(COL[j]),
                           np.full(t.shape, 0.72)], axis=-1)
    patch = PathPatch(ribbon(i, j), facecolor='none', edgecolor='none')
    ax.add_patch(patch)
    im = ax.imshow(rgba, extent=(-R, R, -R, R), origin='lower', interpolation='bilinear', zorder=2)
    im.set_clip_path(patch)

for i, (a0, a1) in enumerate(arcs):
    ax.add_patch(Wedge((0, 0), RING_OUT, a0, a1, width=RING_OUT - RING_IN, facecolor=COL[i],
                       edgecolor=C.WHITE, linewidth=0.8, zorder=3))
    mid = np.radians((a0 + a1) / 2)
    x, y = np.cos(mid), np.sin(mid)
    ha = 'left' if x > 0.2 else 'right' if x < -0.2 else 'center'
    va = 'bottom' if y > 0.35 else 'top' if y < -0.35 else 'center'
    lx, ly = 1.12 * x, 1.12 * y
    # the two smallest arcs sit side by side, so their labels are placed explicitly
    if ITEMS[i] == 'item_sample_size':
        lx, ly, ha, va = 0.20, -1.05, 'left', 'top'
    elif ITEMS[i] == 'item_code_and_data':
        lx, ly, ha, va = 0.915, -0.93, 'left', 'center'
    ax.text(lx, ly, LABEL[i], ha=ha, va=va, fontsize=7.8, color=C.INK, linespacing=0.95,
            clip_on=False)

# ------------------------------------------------------------------ panel B: matrix
CELL, PAD = 0.40, 0.018
MX0, MY_TOP = 4.78, FH - 0.75
offmax = OFF.max()
for i in range(n):
    for j in range(n):
        x0 = MX0 + j * CELL
        y0 = MY_TOP - (i + 1) * CELL
        base = np.array(to_rgb(COL[i]))
        frac = 1.0 if i == j else CO[i, j] / offmax
        rgb = (1 - frac) * np.ones(3) + frac * base
        page.add_patch(Rectangle((x0 + PAD / 2, y0 + PAD / 2), CELL - PAD, CELL - PAD,
                                 facecolor=rgb, edgecolor='none'))
        strong = frac > 0.6                      # full-colour cells carry white text
        ink = C.WHITE if strong else C.INK
        sub_ink = C.WHITE if strong else C.INK_2
        page.text(x0 + CELL / 2, y0 + CELL / 2 + 0.06, f'{CO[i, j]}', ha='center', va='center',
                  fontsize=8.4, fontweight='bold', color=ink)
        page.text(x0 + CELL / 2, y0 + CELL / 2 - 0.085,
                  'total' if i == j else f'{100 * CO[i, j] / CO[i, i]:.0f}%', ha='center',
                  va='center', fontsize=6.6, color=sub_ink)
    page.text(MX0 - 0.06, MY_TOP - (i + 0.5) * CELL, LABEL[i], ha='right', va='center',
              fontsize=7.8, color=C.INK, linespacing=0.95)
for j in range(n):
    page.text(MX0 + (j + 0.62) * CELL, MY_TOP - n * CELL - 0.06, LABEL[j], ha='right', va='top',
              rotation=40, rotation_mode='anchor', fontsize=7.4, color=C.INK, linespacing=0.95)

C.save(fig, 'figure3_cooccurrence')
