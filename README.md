# Methodological evaluation of machine learning clinical prediction models in medical and digital health journals

Data and code for the cross-sectional study by Shaan Patel, Shiva A. Nischal and Hani J. Marcus.
The citation will be added on publication. The study protocol is registered on the Open Science
Framework (doi:[10.17605/OSF.IO/YBXNG](https://doi.org/10.17605/OSF.IO/YBXNG)).

The study appraised 332 machine learning clinical prediction models published between
April 16, 2024 and June 30, 2026 in 10 prespecified journals against seven methodological and
reporting items, and summarised a prespecified three-item composite of validation beyond the
development sample, calibration assessment, and a safeguard against data leakage.

## Contents

```
data/
  included_models.csv              the 332 included models: identifiers, appraisal judgements,
                                   item flags, three-item composite and seven-item score
  excluded_records.csv             the 240 records excluded at full text, with reasons
  clinician_facing_evaluation.csv  clinician-facing evaluation of the 41 models meeting the composite
  README.md                        data dictionary
analysis.py                        reproduces every number in the paper and supplement
figures/                           code for Figures 1-3 and Supplementary Figure 2
```

## Reproducing the results

Requires Python 3.10 or later (the analyses were run in Python 3.12).

```
pip install -r requirements.txt
python analysis.py
python figures/figure1_alluvial.py
python figures/figure2_appraisal_items.py
python figures/figure3_cooccurrence.py
python figures/supplementary_figure2_radar.py
```

`analysis.py` prints the study selection counts, Tables 1 and 2, the results reported in the
text, the seven-item score distribution, the co-occurrence matrix and Supplementary Tables 3 to 6.
Each value is compared with the value reported in the paper, and the script ends with a summary
of how many were reproduced exactly (it exits with an error if any differ).
`python analysis.py --save tables` also writes each table as a CSV file.

The figure scripts write PDF and PNG files to `output/`. They use Liberation Sans, Arimo or Arial
where available and fall back to DejaVu Sans.

## Mapping to the paper

| Paper | Source |
|---|---|
| Supplementary Figure 1 (study selection) | `analysis.py`, study selection section |
| Table 1, Table 2 | `analysis.py` |
| Figure 1 | `figures/figure1_alluvial.py` |
| Figure 2 | `figures/figure2_appraisal_items.py` |
| Figure 3 | `figures/figure3_cooccurrence.py` |
| Supplementary Tables 3 to 5 | `analysis.py` |
| Supplementary Table 6 | `analysis.py`, using `data/clinician_facing_evaluation.csv` |
| Supplementary Figure 2 | `figures/supplementary_figure2_radar.py` |
| Supplementary Table 2 (included studies) | `data/included_models.csv` (`model_no` matches the table) |

The number of records returned by the PubMed search (1,753; Supplementary Table 1) is taken from
the search output; all other selection counts are derived from the data files.

## Licence

Code is released under the MIT licence and the data files under CC BY 4.0 (see `LICENSE`).
