# ATC mapping (Role D)

This notebook gives every drug in the reviews its **ATC class** (the WHO classification of medicines, for example *N06AB = SSRIs*), so the validation step can check whether drugs that patients experience alike also share a class.

## Data

The clean reviews from A (`reviews_clean_deduplicated.parquet`), with 3,671 drug names. The ATC codes come from **RxNorm** (US National Library of Medicine, free RxNav API): it knows the US brand names of Drugs.com and links each one to its active ingredient and its WHO ATC codes.

## What the notebook does

1. **Looks up every drug name in RxNorm**: brand → active ingredient → ATC codes. Every answer is saved in `rxnav_cache.json.gz`, so the notebook runs again without internet.
2. **Fills the gaps**: a name RxNorm does not know takes the codes of the brand or generic name it shares reviews with. A short list checked by hand fixes IUDs (*Mirena*), emergency pills (*Plan B*) and diclofenac gel.
3. **Checks the result**: coverage, unmapped names and a random sample by hand.
4. **Gives one class per drug** for birth control, depression, pain and acne. Some drugs have several codes (clindamycin: acne gel, vaginal cream, antibiotic), so the class that fits the condition is chosen.
5. **Uses the most specific name of each review**: 1,220 Mirena and Kyleena reviews are kept as *Levonorgestrel* in the clean data, so they are classified by the brand in `drug_name_aliases`.

**Main result:** 99.8% of the reviews have an ATC class, and 100% of the reviews for birth control, depression, pain and acne.

## Where the results are

The output files are in the `outputs` folder. They were made from the raw UCI files with A's cleaning rules; with A's files the mapping is the same.

| File | For |
|---|---|
| `scope_review_atc.csv` | Validation: one ATC class per review (birth control, depression, pain, acne) |
| `drug_condition_atc.csv` | Validation: one ATC class per drug and condition |
| `drug_atc_mapping.csv`, `drug_atc_codes.csv` | Everyone: all ATC codes of every drug name |
| `atc_class_names.csv` | Report: names of the ATC classes |
| `role_d_atc_run_stats.json` | Report: all numbers |

## How to use the ATC classes in your own notebook

1. Load the file with this code:

```python
import pandas as pd

review_atc = pd.read_csv('atc-mapping/outputs/scope_review_atc.csv')
```

2. Join it to your results by `review_id`.
3. For the drug, use the column `atc_drug_name`, not `drug_name`: it keeps the brand (*Mirena*) when the clean data kept the generic name.

## To do

- [ ] **Tell A about 9 drug families that mix different medicines** (one review listed under both), for example Sertraline + Lorazepam and Gabapentin + Tramadol. They affect the drug pairs of A6.
- [ ] Agree with A on one name per drug (proposal: `generic_name` from `drug_atc_mapping.csv`).
