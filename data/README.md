# Data dictionary

All files are UTF-8 CSV with a header row.

## included_models.csv

One row per included model (n = 332). Rows are numbered and ordered as in Supplementary Table 2.

| Column | Description |
|---|---|
| `model_no` | Number of the model in Supplementary Table 2 (1 to 332) |
| `first_author`, `year`, `journal`, `pmid`, `title` | Bibliographic details of the article |
| `validation` | Validation strategy: `External`, `Temporal`, or `Internal only` |
| `calibration` | Calibration reported: `Plot`, `Metrics`, or `None` |
| `leakage_safeguard` | Design safeguard against data leakage: `Safeguarded` or `Unclear` |
| `sample_size` | Sample size: `Adequate-justified`, `Adequate-unjustified`, `Not justified`, `Inadequate`, or `Not reported` |
| `outcome_definition` | Outcome definition: `Clearly defined` |
| `code_and_data` | Public availability: `Code and data`, `Code or data only`, or `Neither` |
| `decision_analysis` | Net benefit or decision-curve analysis reported: `Yes` or `No` |
| `reporting_guideline` | Reporting guideline named in the Methods or reference list: `TRIPOD+AI`, `TRIPOD (2015)`, `Other`, `None named`, or `Could not be determined` |
| `appraisal_source` | Source used for appraisal: `Full text`, or `Abstract` where the full text was not retrieved |
| `item_*` | The seven appraisal items, coded 1 if met and 0 otherwise (rules below) |
| `composite` | 1 if all three composite components were met (`item_validation`, `item_calibration`, `item_leakage`) |
| `seven_item_score` | Number of the seven items met (0 to 7) |

Rules for the seven items:

| Item | Met when |
|---|---|
| `item_validation` | `validation` is `External` or `Temporal` |
| `item_calibration` | `calibration` is `Plot` or `Metrics` |
| `item_leakage` | `leakage_safeguard` is `Safeguarded` (an unclear judgement does not meet the item) |
| `item_sample_size` | `sample_size` is `Adequate-justified` |
| `item_outcome` | `outcome_definition` is `Clearly defined` |
| `item_code_and_data` | `code_and_data` is `Code and data` (code or data alone does not meet the item) |
| `item_decision_analysis` | `decision_analysis` is `Yes` |

`analysis.py` re-derives the item flags, composite and score from the judgement columns and
stops if they disagree.

## excluded_records.csv

One row per record excluded after full-text assessment (n = 240), grouped by journal.

| Column | Description |
|---|---|
| `record_no` | Row number |
| `first_author`, `year`, `journal`, `pmid`, `title` | Bibliographic details (PMID missing for some records; the title of record 205 was not recorded and it is identified by PMID) |
| `exclusion_reason` | `Ineligible study type or publication`, `Full text not retrievable`, or `Out of window (published before TRIPOD+AI)` |

## clinician_facing_evaluation.csv

One row per model meeting all three composite components (n = 41), classified by the highest
level of clinician-facing evaluation reported in the eligible publication.

| Column | Description |
|---|---|
| `model_no` | Links to `included_models.csv` |
| `first_author`, `year`, `journal`, `title` | Bibliographic details |
| `category` | `A` live clinical evaluation (model used prospectively within a clinical workflow, or implemented in practice with clinical outcomes reported); `B` human-AI interaction (clinicians made decisions with and without access to model output); `C` standalone comparison with clinicians who did not use the model; `D` offline validation only |
| `initial_category` | Category assigned before full-text review, where full-text review changed it |
| `evidence` | Summary of the evidence in the article supporting the category |

Availability of a web calculator, application or marketed test was not considered clinical
evaluation, and prospective enrolment alone was not classified as clinician-facing evaluation.
