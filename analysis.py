#!/usr/bin/env python3
"""
Reproduces every number reported in the manuscript and supplement from the data in data/.

    python analysis.py                # print all results and check them against the paper
    python analysis.py --save tables  # also write each table as a CSV to ./tables

Each result is compared with the value reported in the paper; the script stops with an
error if any value differs.
"""
import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')

SEARCH_RECORDS = 1753   # records returned by the PubMed search (Supplementary Table 1)

ITEMS = [  # (column, label, in three-item composite)
    ('item_validation', 'Validation beyond the development sample', True),
    ('item_calibration', 'Calibration assessed', True),
    ('item_leakage', 'Leakage safeguard', True),
    ('item_sample_size', 'Sample-size justification', False),
    ('item_outcome', 'Outcome defined', False),
    ('item_code_and_data', 'Code and data available', False),
    ('item_decision_analysis', 'Decision-analytic evaluation', False),
]
JOURNALS = ['npj Digital Medicine', 'Lancet Digital Health', 'JAMA Network Open', 'Nature Medicine',
            'NEJM AI', 'The Lancet', 'Annals of Internal Medicine', 'BMJ', 'JAMA', 'NEJM']

checks = []


def check(label, got, expected):
    """Record a comparison between a computed value and the value reported in the paper."""
    ok = (abs(got - expected) < 1e-9) if isinstance(expected, (int, float)) else (got == expected)
    checks.append((label, got, expected, ok))
    return got


def wilson(k, n, z=1.959963984540054):
    """Wilson score 95% confidence interval for k of n, in percent."""
    if n == 0:
        return float('nan'), float('nan')
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0.0, c - h), 100 * min(1.0, c + h)


def pct(k, n, dp=1):
    return round(100 * k / n, dp)


def fmt_ci(k, n):
    lo, hi = wilson(k, n)
    return f'{k}/{n} ({100 * k / n:.1f}%; 95% CI {lo:.1f}-{hi:.1f})'


def heading(text):
    print('\n' + text + '\n' + '-' * len(text))


def load():
    inc = pd.read_csv(os.path.join(DATA, 'included_models.csv'), dtype={'pmid': str})
    exc = pd.read_csv(os.path.join(DATA, 'excluded_records.csv'), dtype={'pmid': str})
    clin = pd.read_csv(os.path.join(DATA, 'clinician_facing_evaluation.csv'))
    # Derive the seven items from the recorded judgements and confirm the stored flags agree.
    derived = pd.DataFrame({
        'item_validation': inc.validation.isin(['External', 'Temporal']),
        'item_calibration': inc.calibration.isin(['Plot', 'Metrics']),
        'item_leakage': inc.leakage_safeguard.eq('Safeguarded'),
        'item_sample_size': inc.sample_size.eq('Adequate-justified'),
        'item_outcome': inc.outcome_definition.eq('Clearly defined'),
        'item_code_and_data': inc.code_and_data.eq('Code and data'),
        'item_decision_analysis': inc.decision_analysis.eq('Yes'),
    }).astype(int)
    assert (derived == inc[derived.columns]).all().all(), 'item flags disagree with judgements'
    composite = (derived.item_validation & derived.item_calibration & derived.item_leakage).astype(int)
    assert (composite == inc.composite).all(), 'composite disagrees with items'
    assert (derived.sum(axis=1) == inc.seven_item_score).all(), 'score disagrees with items'
    return inc, exc, clin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--save', metavar='DIR', help='write each table as CSV to DIR')
    args = ap.parse_args()
    inc, exc, clin = load()
    N = len(inc)
    tables = {}

    # ------------------------------------------------------------------ selection
    heading('Study selection (Supplementary Figure 1)')
    assessed = N + len(exc)
    print(f'Records identified: {SEARCH_RECORDS}')
    print(f'Excluded at title and abstract: {SEARCH_RECORDS - assessed}')
    print(f'Full-text reports assessed: {assessed}')
    reasons = exc.exclusion_reason.value_counts()
    for r, n in reasons.items():
        print(f'  excluded, {r}: {n}')
    print(f'Included: {N}')
    check('records excluded at title/abstract', SEARCH_RECORDS - assessed, 1181)
    check('full-text reports assessed', assessed, 572)
    check('excluded at full text', len(exc), 240)
    check('excluded: ineligible study type or publication',
          int(reasons.get('Ineligible study type or publication', 0)), 225)
    check('excluded: full text not retrievable', int(reasons.get('Full text not retrievable', 0)), 14)
    check('excluded: out of window', int(reasons.get('Out of window (published before TRIPOD+AI)', 0)), 1)
    check('included models', N, 332)

    # ------------------------------------------------------------------ table 1
    heading('Table 1. Characteristics of included studies')
    jt = inc.journal.value_counts().reindex(JOURNALS, fill_value=0)
    t1 = []
    for j, n in jt.items():
        print(f'{j:30s} {n:4d} ({pct(n, N):.1f}%)')
        t1.append(('Journal', j, n, pct(n, N)))
    for y, n in inc.year.value_counts().sort_index().items():
        print(f'{y:<30d} {n:4d} ({pct(n, N):.1f}%)')
        t1.append(('Publication year', y, n, pct(n, N)))
    for v in ['External', 'Temporal', 'Internal only']:
        n = int((inc.validation == v).sum())
        print(f'{v:30s} {n:4d} ({pct(n, N):.1f}%)')
        t1.append(('Validation', v, n, pct(n, N)))
    tables['table1'] = pd.DataFrame(t1, columns=['characteristic', 'level', 'n', 'percent'])
    for j, n in {'npj Digital Medicine': 230, 'Lancet Digital Health': 38, 'JAMA Network Open': 34,
                 'Nature Medicine': 18, 'NEJM AI': 9, 'The Lancet': 2, 'Annals of Internal Medicine': 1,
                 'BMJ': 0, 'JAMA': 0, 'NEJM': 0}.items():
        check(f'models from {j}', int(jt[j]), n)
    check('journals contributing models', int((jt > 0).sum()), 7)
    for y, n in {2024: 61, 2025: 179, 2026: 92}.items():
        check(f'models published {y}', int((inc.year == y).sum()), n)
    for v, n in {'External': 218, 'Temporal': 9, 'Internal only': 105}.items():
        check(f'validation {v}', int((inc.validation == v).sum()), n)

    # ------------------------------------------------------------------ table 2
    heading('Table 2. Methodological and reporting features')
    expected_items = {'item_validation': 227, 'item_calibration': 50, 'item_leakage': 300,
                      'item_sample_size': 27, 'item_outcome': 332, 'item_code_and_data': 11,
                      'item_decision_analysis': 51}
    t2 = []
    for col, label, comp in ITEMS:
        k = int(inc[col].sum())
        lo, hi = wilson(k, N)
        print(f'{label:42s} {"composite" if comp else "         "}  {fmt_ci(k, N)}')
        t2.append((label, comp, k, pct(k, N), round(lo, 1), round(hi, 1)))
        check(f'{label}, n', k, expected_items[col])
    tables['table2'] = pd.DataFrame(t2, columns=['item', 'in_composite', 'n', 'percent',
                                                 'ci_low', 'ci_high'])
    for label, k, lo, hi in [('validation', 227, 63.2, 73.1), ('calibration', 50, 11.6, 19.3),
                             ('leakage', 300, 86.7, 93.1), ('sample size', 27, 5.6, 11.6),
                             ('outcome', 332, 98.9, 100.0), ('code and data', 11, 1.9, 5.8),
                             ('decision analysis', 51, 11.9, 19.6)]:
        w = wilson(k, N)
        check(f'{label} CI', (round(w[0], 1), round(w[1], 1)), (lo, hi))

    # ------------------------------------------------------------------ composite
    heading('Prespecified three-item composite')
    met = int(inc.composite.sum())
    print(f'Met all three components:     {fmt_ci(met, N)}')
    print(f'Did not meet all three:       {fmt_ci(N - met, N)}')
    check('composite met', met, 41)
    check('composite met CI', tuple(round(x, 1) for x in wilson(met, N)), (9.2, 16.3))
    check('composite not met CI', tuple(round(x, 1) for x in wilson(N - met, N)), (83.7, 90.8))
    v = inc.item_validation == 1
    vl = v & (inc.item_leakage == 1)
    vlc = vl & (inc.item_calibration == 1)
    print(f'Validated beyond development sample: {int(v.sum())}')
    print(f'  ... with a leakage safeguard: {int(vl.sum())} ({pct(vl.sum(), v.sum()):.1f}%)')
    print(f'  ... of these, calibration assessed: {int(vlc.sum())} ({pct(vlc.sum(), vl.sum()):.1f}%); '
          f'not assessed: {int((vl & ~(inc.item_calibration == 1)).sum())} '
          f'({pct((vl & (inc.item_calibration == 0)).sum(), vl.sum()):.1f}%)')
    check('validated and leakage safeguard', int(vl.sum()), 222)
    check('validated + leakage, % of validated', pct(vl.sum(), v.sum()), 97.8)
    check('... and calibration assessed', int(vlc.sum()), 41)
    check('... calibration assessed, %', pct(vlc.sum(), vl.sum()), 18.5)
    check('... calibration not assessed', int((vl & (inc.item_calibration == 0)).sum()), 181)
    check('... calibration not assessed, %', pct((vl & (inc.item_calibration == 0)).sum(), vl.sum()), 81.5)
    other = N - met - int((vl & (inc.item_calibration == 0)).sum())
    print(f'Validation or leakage criterion not met: {other} ({pct(other, N):.1f}%)')
    check('validation or leakage not met', other, 110)

    # ------------------------------------------------------------------ score
    heading('Seven-item score (Figure 2B)')
    s = inc.seven_item_score
    dist = s.value_counts().reindex(range(8), fill_value=0)
    met_by = inc[inc.composite == 1].seven_item_score.value_counts().reindex(range(8), fill_value=0)
    for k in range(8):
        print(f'  score {k}: {dist[k]:4d}   (meeting composite: {met_by[k]})')
    q1, q3 = np.percentile(s, [25, 75])
    print(f'Median {s.median():.0f} (IQR {q1:.0f}-{q3:.0f}); mean {s.mean():.2f} (SD {s.std(ddof=1):.2f}); '
          f'range {s.min()}-{s.max()}')
    check('score distribution', dist.tolist(), [0, 23, 70, 151, 63, 20, 5, 0])
    check('composite models by score', met_by.tolist(), [0, 0, 0, 0, 21, 15, 5, 0])
    check('score median', float(s.median()), 3.0)
    check('score IQR', (float(q1), float(q3)), (2.0, 4.0))
    check('score mean', round(s.mean(), 2), 3.01)
    check('score SD', round(s.std(ddof=1), 2), 1.03)
    check('score range', (int(s.min()), int(s.max())), (1, 6))
    check('models meeting all seven items', int((s == 7).sum()), 0)
    check('models with the highest score (6)', int((s == 6).sum()), 5)

    # ------------------------------------------------------------------ co-occurrence
    heading('Co-occurrence of appraisal items (Figure 3)')
    six = ['item_validation', 'item_calibration', 'item_leakage', 'item_sample_size',
           'item_code_and_data', 'item_decision_analysis']
    M = inc[six].to_numpy()
    C = M.T @ M
    names = ['Validation', 'Calibration', 'Leakage', 'Sample size', 'Code+data', 'Decision']
    co = pd.DataFrame(C, index=names, columns=names)
    print(co.to_string())
    tables['figure3_cooccurrence'] = co
    check('co-occurrence matrix', C.tolist(),
          [[227, 41, 222, 21, 8, 45], [41, 50, 49, 10, 2, 19], [222, 49, 300, 24, 9, 49],
           [21, 10, 24, 27, 1, 9], [8, 2, 9, 1, 11, 1], [45, 19, 49, 9, 1, 51]])

    # ------------------------------------------------------------------ supplementary table 3
    heading('Supplementary Table 3. Methodological evaluation by journal')
    t3 = []
    for j in JOURNALS:
        g = inc[inc.journal == j]
        if len(g) == 0:
            print(f'{j:30s}    0')
            t3.append((j, 0, None, None, None, None))
            continue
        sd = g.seven_item_score.std(ddof=1) if len(g) > 1 else float('nan')
        row = (j, len(g), int(g.composite.sum()), pct(g.composite.sum(), len(g)),
               round(g.seven_item_score.mean(), 2), None if math.isnan(sd) else round(sd, 2),
               pct(g.item_calibration.sum(), len(g)))
        t3.append((row[0], row[1], row[2], row[4], row[5], row[6]))
        sd_txt = 'NA' if math.isnan(sd) else f'{sd:.2f}'
        print(f'{j:30s} {len(g):4d}  composite {row[2]:3d} ({row[3]:5.1f}%)  '
              f'mean {row[4]:.2f} (SD {sd_txt})  calibration {row[6]:.1f}%')
    tables['supp_table3'] = pd.DataFrame(t3, columns=['journal', 'n', 'composite_n', 'mean_score',
                                                      'sd_score', 'calibration_percent'])
    exp3 = {'npj Digital Medicine': (24, 2.88, 1.04, 12.6), 'Lancet Digital Health': (7, 3.47, 1.13, 18.4),
            'JAMA Network Open': (6, 3.15, 0.96, 26.5), 'Nature Medicine': (2, 3.00, 0.49, 11.1),
            'NEJM AI': (0, 3.22, 0.44, 0.0), 'The Lancet': (2, 4.50, 0.71, 100.0),
            'Annals of Internal Medicine': (0, 4.00, None, 100.0)}
    for j, (c, m, sd, cal) in exp3.items():
        g = inc[inc.journal == j]
        check(f'{j}: composite', int(g.composite.sum()), c)
        check(f'{j}: mean score', round(g.seven_item_score.mean(), 2), m)
        if sd is not None:
            check(f'{j}: SD', round(g.seven_item_score.std(ddof=1), 2), sd)
        check(f'{j}: calibration %', pct(g.item_calibration.sum(), len(g)), cal)
    big = [j for j in JOURNALS if (inc.journal == j).sum() >= 10]
    check('journals with at least 10 models', big,
          ['npj Digital Medicine', 'Lancet Digital Health', 'JAMA Network Open', 'Nature Medicine'])

    # ------------------------------------------------------------------ supplementary table 4
    heading('Supplementary Table 4. Reporting guideline use')
    t4 = []
    order = ['TRIPOD+AI', 'TRIPOD (2015)', 'Other', 'None named', 'Could not be determined']
    for gname in order:
        g = inc[inc.reporting_guideline == gname]
        print(f'{gname:26s} {len(g):4d} ({pct(len(g), N):4.1f}%)  composite {int(g.composite.sum()):3d} '
              f'({pct(g.composite.sum(), len(g)):.1f}%)  mean score {g.seven_item_score.mean():.2f}')
        t4.append((gname, len(g), pct(len(g), N), int(g.composite.sum()),
                   pct(g.composite.sum(), len(g)), round(g.seven_item_score.mean(), 2)))
    named = inc[inc.reporting_guideline.isin(['TRIPOD+AI', 'TRIPOD (2015)', 'Other'])]
    print(f'{"Any named guideline":26s} {len(named):4d} ({pct(len(named), N):4.1f}%)  composite '
          f'{int(named.composite.sum()):3d} ({pct(named.composite.sum(), len(named)):.1f}%)  '
          f'mean score {named.seven_item_score.mean():.2f}')
    t4.append(('Any named guideline', len(named), pct(len(named), N), int(named.composite.sum()),
               pct(named.composite.sum(), len(named)), round(named.seven_item_score.mean(), 2)))
    tables['supp_table4'] = pd.DataFrame(t4, columns=['guideline', 'n', 'percent', 'composite_n',
                                                      'composite_percent', 'mean_score'])
    exp4 = {'TRIPOD+AI': (13, 4, 3.62), 'TRIPOD (2015)': (7, 3, 3.57), 'Other': (6, 0, 2.67),
            'None named': (299, 34, 2.97), 'Could not be determined': (7, 0, 3.29)}
    for gname, (n, c, m) in exp4.items():
        g = inc[inc.reporting_guideline == gname]
        check(f'guideline {gname}: n', len(g), n)
        check(f'guideline {gname}: composite', int(g.composite.sum()), c)
        check(f'guideline {gname}: mean score', round(g.seven_item_score.mean(), 2), m)
    check('any named guideline: n', len(named), 26)
    check('any named guideline: composite', int(named.composite.sum()), 7)
    check('any named guideline: mean score', round(named.seven_item_score.mean(), 2), 3.38)

    # ------------------------------------------------------------------ supplementary table 5
    heading('Supplementary Table 5. Robustness analyses')
    t5 = []
    primary = met
    independent = int(((inc.validation == 'External') & (inc.item_calibration == 1)
                       & (inc.item_leakage == 1)).sum())
    unclear_ok = int((inc.item_validation & inc.item_calibration).sum())
    nonnpj = inc[inc.journal != 'npj Digital Medicine']
    relaxed = inc.code_and_data.isin(['Code and data', 'Code or data only']).astype(int)
    relaxed_score = inc.seven_item_score - inc.item_code_and_data + relaxed
    for label, k, n in [('Primary analysis', primary, N),
                        ('Independent validation only', independent, N),
                        ('Unclear leakage treated as meeting criterion', unclear_ok, N),
                        ('Excluding npj Digital Medicine', int(nonnpj.composite.sum()), len(nonnpj)),
                        ('Reproducibility defined as code or data', primary, N)]:
        lo, hi = wilson(k, n)
        print(f'{label:46s} {fmt_ci(k, n)}')
        t5.append((label, k, n, pct(k, n), round(lo, 1), round(hi, 1)))
    print(f'  code or data available: {int(relaxed.sum())} ({pct(relaxed.sum(), N):.1f}%); '
          f'mean seven-item score {relaxed_score.mean():.2f}; meeting all seven items: '
          f'{int((relaxed_score == 7).sum())}')
    tables['supp_table5'] = pd.DataFrame(t5, columns=['analysis', 'met', 'n', 'percent', 'ci_low',
                                                      'ci_high'])
    check('independent validation only', independent, 39)
    check('independent validation CI', tuple(round(x, 1) for x in wilson(independent, N)), (8.7, 15.7))
    check('unclear leakage as met', unclear_ok, 41)
    check('excluding npj: composite', int(nonnpj.composite.sum()), 17)
    check('excluding npj: n', len(nonnpj), 102)
    check('excluding npj: CI', tuple(round(x, 1) for x in wilson(17, 102)), (10.7, 25.1))
    check('code or data: percent', pct(relaxed.sum(), N), 73.2)
    check('code or data: mean score', round(relaxed_score.mean(), 2), 3.70)
    check('code or data: models meeting all seven', int((relaxed_score == 7).sum()), 5)

    # ------------------------------------------------------------------ supplementary table 6
    heading('Supplementary Table 6. Clinician-facing evaluation (models meeting the composite)')
    n41 = len(clin)
    assert set(clin.model_no) == set(inc.loc[inc.composite == 1, 'model_no']), \
        'clinician-facing file must cover exactly the models meeting the composite'
    cats = clin.category.value_counts().reindex(['A', 'B', 'C', 'D'], fill_value=0)
    labels = {'A': 'Live clinical evaluation', 'B': 'Human-AI interaction',
              'C': 'Standalone clinician comparison', 'D': 'Offline validation only'}
    t6 = []
    for c, n in cats.items():
        print(f'{c}. {labels[c]:34s} {n:3d} ({pct(n, n41):.1f}%)')
        t6.append((c, labels[c], n, pct(n, n41)))
    anyc = int(cats[['A', 'B', 'C']].sum())
    used = int(cats[['A', 'B']].sum())
    print(f'Any clinician contact (A-C): {anyc} ({pct(anyc, n41):.1f}%)')
    print(f'Used by clinicians (A-B):    {used} ({pct(used, n41):.1f}%)')
    tables['supp_table6'] = pd.DataFrame(t6, columns=['category', 'label', 'n', 'percent'])
    check('clinician-facing categories', cats.tolist(), [2, 2, 3, 34])
    check('any clinician contact', anyc, 7)
    check('any clinician contact %', pct(anyc, n41), 17.1)
    check('used by clinicians', used, 4)
    check('used by clinicians %', pct(used, n41), 9.8)
    check('offline only %', pct(cats['D'], n41), 82.9)

    # ------------------------------------------------------------------ result
    heading('Check against the reported values')
    bad = [c for c in checks if not c[3]]
    for label, got, exp, ok in bad:
        print(f'MISMATCH  {label}: computed {got}, reported {exp}')
    print(f'{len(checks) - len(bad)} of {len(checks)} reported values reproduced exactly.')

    if args.save:
        os.makedirs(args.save, exist_ok=True)
        for name, t in tables.items():
            t.to_csv(os.path.join(args.save, f'{name}.csv'), index=name == 'figure3_cooccurrence')
        print(f'Tables written to {args.save}/')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
