"""Shared data loading, style and output settings for the figure scripts."""
import os

import matplotlib as mpl
import pandas as pd

mpl.use('Agg')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'output')

mpl.rcParams.update({
    'font.family': 'sans-serif',
    # Liberation Sans, Arimo and Arial share the same metrics; DejaVu Sans is the fallback
    'font.sans-serif': ['Liberation Sans', 'Arimo', 'Arial', 'Helvetica', 'DejaVu Sans'],
    'pdf.fonttype': 42,      # embed TrueType so text remains editable
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
    'axes.linewidth': 0.6,
})

# text
INK = '#1d1d1b'
INK_2 = '#52514e'
MUTED = '#6f6e69'
RULE = '#c3c2b7'
GRID = '#e1e0d9'
TRACK = '#efeee9'
WHITE = '#ffffff'

# composite status (Figures 1 and 2)
BLUE_DEEP = '#1c5cab'     # met all three composite components
BLUE_LIGHT = '#6da7ec'    # composite component / validation and leakage safeguard only
GREY = '#c3c2b7'          # other
GREY_LIGHT = '#dddcd5'

# appraisal items (Figure 3) and journals (Supplementary Figure 2)
ITEM_COLOR = {
    'item_validation': '#374E55',
    'item_calibration': '#B24745',
    'item_leakage': '#00A1D5',
    'item_sample_size': '#DF8F44',
    'item_code_and_data': '#6A6599',
    'item_decision_analysis': '#79AF97',
}
JOURNAL_COLOR = {
    'npj Digital Medicine': '#374E55',
    'Lancet Digital Health': '#00A1D5',
    'JAMA Network Open': '#DF8F44',
    'Nature Medicine': '#B24745',
}


def load():
    """One row per included model (see data/README.md)."""
    return pd.read_csv(os.path.join(ROOT, 'data', 'included_models.csv'), dtype={'pmid': str})


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    pdf = os.path.join(OUT, f'{name}.pdf')
    png = os.path.join(OUT, f'{name}.png')
    fig.savefig(pdf)
    fig.savefig(png, dpi=600)
    print(f'wrote {os.path.relpath(pdf, ROOT)} and {os.path.relpath(png, ROOT)}')
