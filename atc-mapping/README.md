# ATC mapping (Role D · Enrich)

This notebook gives every drug name in the reviews its **ATC class** (Anatomical Therapeutic Chemical classification of the WHO, for example *N06AB = SSRIs*). The validation step uses it to check whether drugs that patients experience alike also share a pharmacological class (research question 3).

## Which source, and why

The project plan left this open. We use **RxNorm** (US National Library of Medicine), through its free **RxNav API**:

- Drugs.com is a US site, so most names are US brands (*Nexplanon*, *Sprintec*). RxNorm knows them and links each one to its active ingredient.
- RxNorm stores the **WHO ATC codes** of each ingredient. One source does both steps.
- The WHO index itself has no download or API; Wikidata and ChEMBL know few brand names.

## What the notebook does

1. **Loads A's clean data** (`reviews_clean_deduplicated.parquet`, `drug_families.csv`). Without them it rebuilds the part it needs from the raw UCI files with A's own rules (A2–A3).
2. **Lists all 3,671 drug names** (brands and generics, from `drug_name_aliases`).
3. **Looks up every name in RxNorm**: name → active ingredient (or combination) → ATC codes. It also finds brands no longer sold (*Implanon*, *Belviq*) and names with formulation words (*Effexor XR*). Every API answer is saved in `rxnav_cache.json.gz`, so the notebook runs again without internet.
4. **Fills the gaps**: a name RxNorm cannot map takes the codes of the brand or generic name it is listed with on the same reviews (A3). A short list checked by hand fixes products where the ingredient code is wrong: IUDs (*Mirena*, *Skyla*, *Kyleena*, copper IUD), emergency pills (*Plan B*) and topical diclofenac (*Voltaren Gel*).
5. **Checks**: coverage, A's families that join different medicines, unmapped names, random sample by hand.
6. **One class per review and per drug** for the four conditions in scope. Some drugs have several codes (clindamycin: acne gel, vaginal cream, antibiotic), so the class that fits the condition is chosen (acne → D10/J01, pain → N02/M01, ...).

**Main result:** 99.8% of the 128,751 reviews have an ATC class; 100% of the reviews for birth control, depression, pain and acne.

| Condition | Drug names | ATC classes (level 4) | Biggest classes |
|---|---|---|---|
| Birth Control | 88 | 6 | combined pills (G03AA), progestogens (G03AC), IUDs (G02BA), vaginal ring (G02BB) |
| Depression | 94 | 16 | other antidepressants (N06AX), SSRIs (N06AB), antipsychotics (N05A) |
| Pain | 141 | 31 | opioid combinations (N02AJ), opium alkaloids (N02AA), other opioids (N02AX), NSAIDs (M01AB), gabapentinoids (N02BF) |
| Acne | 77 | 17 | topical retinoids (D10AD), tetracyclines (J01AA), pills (G03AA), isotretinoin (D10BA), topical anti-infectives (D10AF) |

## Two things the team should know

1. **Many Mirena reviews are named "Levonorgestrel" in the clean data.** A3 keeps one name per review, often the generic one. 1,220 birth-control reviews of the IUDs Mirena and Kyleena are kept as *Levonorgestrel*, whose ATC codes are the pill ones. The brand is still in `drug_name_aliases`, so `scope_review_atc.csv` classifies each review by its **most specific name** (`atc_drug_name`). For drug profiles, use `atc_drug_name`, not `drug_name`.
2. **9 of A's drug families join different medicines** (one review listed under both): *Sertraline + Lorazepam*, *Duloxetine + Pregabalin + Lurasidone*, *Gabapentin + Tramadol*, *Quetiapine + Fluvoxamine*, *Acetaminophen / hydrocodone + Triazolam*, and 4 small ones. A6 counts each family as one medicine, so these pairs can never appear as similar stories. The ATC mapping does not use families for this reason.

## Where the results are

All files are in [`outputs/`](outputs/) (small enough for the repository, so nobody needs to run the API again).

| File | One row per | For |
|---|---|---|
| `drug_atc_mapping.csv` | drug name (3,671) | ATC codes and classes of any name; `generic_name` = **one name per medicine** |
| `drug_atc_codes.csv` | (drug name, ATC code) | analyses that keep all codes of a drug |
| `drug_condition_atc.csv` | (condition in scope, drug) | **the validation**: one ATC class per drug, with `n_reviews` |
| `scope_review_atc.csv` | review in scope (36,385) | joining ATC to the clusters by `review_id` |
| `atc_class_names.csv` | ATC class | class names for tables and figures |
| `role_d_atc_run_stats.json` | – | all numbers for the report |
| `rxnav_cache.json.gz` | API request | running the notebook offline |

## How to use the results

```python
import pandas as pd

# one ATC class per review in scope (birth control, depression, pain, acne)
review_atc = pd.read_csv('atc-mapping/outputs/scope_review_atc.csv')
clusters_with_atc = clusters.merge(review_atc, on='review_id')       # clusters: one row per review_id

# one ATC class per drug and condition
drug_atc = pd.read_csv('atc-mapping/outputs/drug_condition_atc.csv')
```

Compare drugs at **level 4** (`atc_level_4`, e.g. SSRIs) and level 3 (`atc_level_3`, e.g. antidepressants). Drugs without a class (0.2% of reviews) are left out of the validation.

## How to run the notebook

- **Kaggle**: add A's notebook *Clean and deduplicate* as input (*Add Input → Notebook Output*) and either turn on *Settings → Internet* or add `rxnav_cache.json.gz` as input.
- **Locally**: put `drugsComTrain_raw.tsv` and `drugsComTest_raw.tsv` (UCI Drug Review dataset, [drugsCom_raw.zip](https://archive.ics.uci.edu/ml/machine-learning-databases/00462/drugsCom_raw.zip)) in `data/raw/` at the root of the repository (ignored by git), then run `atc-mapping.ipynb` from this folder. With the cache it takes about 30 seconds.

The outputs in this folder were made locally from the raw UCI files (A2–A3 rebuilt). On Kaggle, with A's files, the mapping is identical; only the review counts can differ by the 87 near-duplicates A4 removes.

## To do

- [ ] Agree with A on one name per drug: proposal `generic_name` from `drug_atc_mapping.csv` for "same medicine", `atc_drug_name` for product-level profiles.
- [ ] Tell A about the 9 families that join different medicines (affects A6's drug-to-drug table).
- [ ] Validation vs ATC (Nov 16–27): drug experience profiles from B's clusters, profile similarity vs shared ATC class, rating prediction.
