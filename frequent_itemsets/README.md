# Frequent itemsets (Role E)

This notebook turns every patient review into a **basket** of side effects and finds the side effects that are reported together. It uses A-priori and PCY (the course topic *frequent itemsets*, both written from scratch) and association rules with a significance test. It answers research question 2: *which side effects co-occur, and do the combinations differ between drugs for the same condition?*

## Data

Role A's output: `reviews_clean_deduplicated.parquet` (128,663 clean reviews) and `drug_families.csv` (brand and generic names of the same medicine). We use the 36,365 reviews of the four conditions of the project plan: **Birth Control, Depression, Pain and Acne**.

## What the notebook does

1. **E1 · Loads the clean reviews**, gives every drug one family name (Nexplanon = Etonogestrel) and keeps the four conditions.
2. **E2 · Side-effect lexicon** (`side_effect_lexicon.json`): 57 concepts and 450 ways patients write them (*"couldn't sleep"*, *"gained 20 lbs"*). It was built in three versions:
   - v1, by hand;
   - v2, from the 300 most frequent phrases of negative reviews with no side effect found (`lexicon/lexicon_expansion_candidates_filled.xlsx`);
   - v3, after an error review.

   On 80 blind reviews not used to build it: **precision 0.74, recall 0.67**. The gold labels were annotated by an LLM, blind to the extractor, so these numbers are indicative. On the 10,221 negative reviews in scope (rating ≤ 4), the share with at least one side effect grows from 80.1 % (v1) to 83.2 % (v2) and 83.6 % (v3).

   The notebook starts with a short section, *Which lexicon, and why*, that explains why we built our own lexicon of lay phrasings instead of matching MedDRA/SIDER terms or training a classifier.
3. **E3 · Extractor**: finds the lexicon phrases with regular expressions and drops mentions that are:
   - negated (*"no nausea"*, NegEx-style, 5-word window, a clause ends at punctuation and *but*);
   - hypothetical (*"worried about weight gain"*);
   - the condition being treated (acne in Acne).
4. **E4 · Baskets** of the 36,365 reviews: 104,986 mentions, 73,948 kept (12.7 % dropped as negated, 0.5 % as hypothetical, 18.1 % as the treated condition). 72 % of the reviews report at least one side effect (mean basket 1.72; 2.38 if not empty). Empty baskets are kept, because they count in N. Reviews with more side effects get lower ratings (Birth Control: 7.5 with none, 5.2 with 3 or more). Also a side-effect profile per condition and per drug.
5. **E5 · Support threshold**: sensitivity analysis with 0.25 %, 0.5 %, 1 % and 2 %. At 1 % Pain keeps only one pair; at 0.25 % Birth Control explodes (about 200 pairs and 200 triples). Chosen: an itemset is frequent if at least **max(0.5 % of the condition's reviews, 20)** reviews report it (98 / 36 / 26 / 23 reviews in Birth Control / Depression / Pain / Acne).
6. **E6 · A-priori from scratch**: triangular array, join + prune. The output is checked against brute-force counting inside the notebook. Result: 126 frequent items, 209 pairs and 86 triples (all triples are in Birth Control).
7. **E7 · PCY from scratch**: hash buckets and a bitmap. It gives exactly the same itemsets as A-priori in the four conditions, and its bitmap removes 80-98 % of the candidate pairs.
8. **E8 · Benchmark A-priori vs PCY** on the baskets of the four conditions (median of 5 runs, 10,000 buckets, plus a sweep of the number of buckets). With our 57 items, A-priori is better: PCY is **1.8× slower** and has no memory to save, because A-priori's pass 2 needs at most 3 KB. PCY would only pay off with thousands of frequent items, and only if it removes at least 2/3 of the candidate pairs. With too few buckets (100) almost every bucket is frequent and the filter removes nothing.
9. **E9 · Association rules**: support, confidence, lift and interest, ranked by lift, with Fisher's exact test and Benjamini-Hochberg (FDR 5 %). Of 934 rules, 530 pass confidence ≥ 0.1, 443 also lift > 1 and **391** also q < 0.05. A network per condition shows the groups of side effects that go together.
10. **E10 · Do combinations differ between drugs?** Each pair is measured inside every drug with at least 200 reviews (39 drugs, 2,443 drug × pair tests, 550 significant). Of the 127 pairs associated at condition level:
    - 22 are **universal**: lift > 1 in every drug of the condition;
    - 98 are **drug-specific**: reported together significantly more often with one drug (q < 0.05, odds ratio > 1), and going together inside that drug (`lift_other_drugs` is shown to catch pairs that are only frequent because one effect is common with that drug).

    The lifts are similar in short and long reviews, so the associations are not just patients who list everything.
11. **Summary for the report**: printed from the run and saved in `role_e_run_stats.json`, so the numbers always match the outputs.

**Main result:** side-effect baskets for 36,365 reviews (`baskets.parquet`) and a profile of every drug (`drug_side_effect_profiles.csv`, for D). Some side-effect pairs belong to the whole condition. Others are specific to one medicine, mostly in hormonal contraceptives and isotretinoin.

## What is in this folder

| Path | What it is | Used by the notebook |
|---|---|---|
| `frequent-itemsets.ipynb` | The whole analysis, step by step | |
| `side_effect_lexicon.json` | Lexicon v3 (57 concepts, 450 variants) | Yes |
| `lexicon/side_effect_lexicon_v1.json`, `side_effect_lexicon_v2.json` | The two earlier versions, to compare coverage | Yes |
| `lexicon/lexicon_expansion_candidates_filled.xlsx` | The 300 phrases reviewed by hand to build v2 | Yes |
| `lexicon/validation_sample_annotated.xlsx` | Evidence for v3: 200 reviews with the side effects each one really reports (`gold_basket`) | No, cited in E2 |
| `lexicon/validation_round2_annotated.xlsx` | Evidence for the precision 0.74 and recall 0.67: 80 new reviews, **annotated by an LLM (Claude)** that saw only the review text, not the extractor's output | No, cited in E2 |
| `data/reviews_clean_deduplicated.parquet`, `data/drug_families.csv` | Role A's output (copy it here, or add A's notebook output on Kaggle) | Yes |
| `outputs/` | Created by the notebook. Only `baskets.parquet` and `drug_side_effect_profiles.csv` are committed (the validation step reads them); the rest is regenerated in about 30 s | |
| `../.gitignore` | `data/` (Role A's data) is not committed, and neither is the rest of `outputs/` | |

## Where the results are

| File | For |
|---|---|
| `outputs/baskets.parquet` | Everyone: one basket of side effects per review |
| `outputs/drug_side_effect_profiles.csv` | ATC mapping (D): % of each drug's reviews that report each side effect |
| `outputs/frequent_itemsets.csv`, `rules_by_condition.csv` | Report: frequent itemsets and rules of the 4 conditions |
| `outputs/rules_by_drug.csv`, `pair_classification.csv` | Report (RQ2), D: pairs per drug, universal vs drug-specific |
| `outputs/benchmark.csv` | Report: A-priori vs PCY |
| `outputs/role_e_run_stats.json`, `outputs/figures/` | Report: all numbers and figures (`condition_concept_heatmap`, `rating_by_n_side_effects`, `support_sensitivity`, `benchmark_real`, `cooccurrence_networks`, `drug_lift_heatmap_birth_control`, `drug_specific_pairs`) |

## How to use the baskets / profiles in your own notebook

```python
from pathlib import Path
import pandas as pd

folder = next(p for p in [Path('/kaggle/input'), Path('../frequent_itemsets/outputs')] if p.exists())
baskets = pd.read_parquet(next(folder.rglob('baskets.parquet')))
profiles = pd.read_csv(next(folder.rglob('drug_side_effect_profiles.csv')))
```

- `baskets`: one row per review, with `review_id`, `condition_name`, `drug_family`, `rating` and `basket`. `basket` is the list of side-effect concepts and can be empty. Join it to other tables on `review_id`.
- `profiles`: one row per drug family × condition. Each concept column is the % of the drug's reviews that report it.

## How to run

Put Role A's two files in `data/` (or add A's notebook output on Kaggle), then **Restart & Run All** (about 30 seconds to 2 minutes). All parameters are in section *0 · Setup and parameters*. The notebook needs numpy, pandas, pyarrow, scipy, matplotlib and openpyxl (to read the lexicon spreadsheet); networkx is optional and only used for the co-occurrence networks.

**Reproducibility check (25 Nov).** A rerun from the raw UCI data (through A's notebook) gives exactly the numbers of the summary above; only the benchmark times depend on the machine (PCY 1.6× instead of 1.8× slower).

## To do

- [x] Share `drug_side_effect_profiles.csv` with D and agree on the drug names. The validation step builds its own profiles from `baskets.parquet` per active ingredient (D's `generic_name`), so A's mixed families do not mix two medicines.
- [ ] Write the Role E section of the report from `role_e_run_stats.json` and the figures.
