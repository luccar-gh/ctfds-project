# Validation (Role D)

This notebook is stage 5 of the pipeline. It answers the last two research questions:

- **RQ3** · *Which drugs do patients experience similarly, regardless of official classification?* Every drug gets an **experience profile**, drugs are compared by profile, and the result is checked against the **ATC classes** of D's mapping.
- **RQ4** · *Does the type of experience a patient reports predict their rating?* B8 showed that the mean rating differs between B's clusters; here a model predicts a high or low rating from the cluster, against a baseline and against "only knowing the drug".

## Data

The outputs of the other roles, joined on `review_id` (36,360 reviews of Birth Control, Depression, Pain and Acne):

| File | From | Locally | On Kaggle |
|---|---|---|---|
| `cluster_assignments.parquet` | B | `../clustering/outputs` (in the repo) | B's notebook output |
| `scope_review_atc.csv`, `atc_class_names.csv` | D | `../atc-mapping/outputs` (in the repo) | D's notebook output |
| `baskets.parquet` | E | `../frequent_itemsets/outputs` (**not in the repo**: run E's notebook first) | E's notebook output |
| `cluster_labels_final.csv` (optional) | C | `../nlp-embeddings/outputs` (in the repo) | C's notebook output |
| `embeddings_masked_v2_all.npy` + `_ids.parquet` (optional) | C | not in the repo (395 MB) | C's Kaggle dataset |

Without C's embeddings the notebook runs everything except the optional *meaning* view.

## What the notebook does

1. **D7 · Load and join** the outputs of B, D and E.
2. **D8 · One identity per drug**: the active ingredient (`generic_name` from D's mapping), so *Zoloft* and *Sertraline* are one drug, and A's families that mix two medicines (*Gabapentin* + Tramadol, *Duloxetine* + Pregabalin) are split. An ingredient with two classes in a condition gets the class in its name (*diclofenac (M02AA)* gel vs *diclofenac (M01AB)* tablet). Drugs with at least 50 reviews in the condition are compared: 15 in Birth Control, 24 in Depression, 27 in Pain, 15 in Acne (91-100 % of the reviews).
3. **D9 · Experience profiles**:
   - **side effects**: % of the drug's reviews that report each side effect (E's baskets);
   - **experience types**: % of the drug's reviews in each of B's clusters, without the clusters where one drug has ≥ 50 % of the reviews (those clusters are a drug name, not an experience: 27 of B's 100 clusters);
   - two robustness checks of the side-effect profiles: **z-scored** (rare side effects weigh as much as common ones) and **composition** (which side effects, not how many);
   - optional **meaning**: the mean of C's masked Sentence-BERT embeddings of the drug's reviews.
4. **D10 · Similarity between drugs**: *centred cosine* (the condition's mean profile is subtracted first, so two drugs are similar when they differ from the average drug in the same direction), and a map of the drugs by hierarchical clustering (average linkage), shown as heatmaps.
5. **D11 · Agreement with ATC**, with a null model of 10,000 random shuffles of the classes among the drugs:
   - **same-class gap**: mean similarity of same-class pairs minus different-class pairs (main test, Benjamini-Hochberg over all tests);
   - **nearest neighbour**: is each drug's most similar drug in the same class?
   - **ARI** between the drug tree and the classes.
6. **D12 · Exceptions**: drugs of different classes that patients describe alike, and drugs of one class that they describe differently, with the side effects that explain each pair (drugs with ≥ 100 reviews).
7. **D13 · Rating prediction**: high (≥ 7) vs low (≤ 4) rating, logistic regression, 5-fold cross-validation, ROC AUC and balanced accuracy, for the drug alone, B's experience type, E's side effects and their combinations.
8. **D14 · Save** the tables, figures and `role_d_validation_run_stats.json`, and print the summary for the report.

## Main results

**RQ3 · Drugs of the same ATC class do feel alike, in all four conditions.** Side-effect profiles, ATC level 4:

| Condition | Drugs | Same-class gap | q | Nearest drug in same class (chance) |
|---|---|---|---|---|
| Birth Control | 15 | +0.60 | < 0.001 | 93 % (41 %) |
| Depression | 24 | +0.14 | 0.006 | 53 % (29 %) |
| Pain | 27 | +0.33 | 0.001 | 44 % (7 %) |
| Acne | 15 | +0.92 | < 0.001 | 55 % (14 %) |

The result holds with B's experience types, with z-scored and composition profiles, and at ATC level 3: 31 of the 32 tests have q < 0.05. The exception is Pain with experience types at level 3 (q = 0.07). The drug map recovers the classes best in Birth Control (ARI 0.81): IUDs, combined pills and progestogen-only methods form separate blocks. Depression has the weakest gap, because ATC's *N06AX Other antidepressants* mixes very different drugs. Inside N06AX the patients separate the SNRIs (venlafaxine, desvenlafaxine, duloxetine) from mirtazapine.

**Exceptions worth reporting** (different class, experienced alike):

- *mirtazapine* (N06AX) and *quetiapine* (N05AH), similarity 0.87: weight gain and drowsiness, both sedating antihistaminic drugs.
- *venlafaxine* (SNRI) and *paroxetine* (SSRI): withdrawal and dizziness, both known for discontinuation symptoms.
- *NuvaRing* (G02BB, vaginal ring) and *Xulane* (G03AA, patch): fewer cramps, less acne and spotting than the pills. Both are non-oral combined methods.
- *methadone* (N07BC, used for opioid dependence) and *oxycodone* (N02AA): patients describe methadone as an opioid painkiller.

**RQ4 · The type of experience predicts the rating, beyond the drug.** ROC AUC, high vs low rating:

| Features | Birth Control | Depression | Pain | Acne |
|---|---|---|---|---|
| drug only | 0.58 | 0.62 | 0.71 | 0.66 |
| experience type (B) | 0.69 | 0.66 | 0.67 | 0.68 |
| side effects (E) | 0.76 | 0.67 | 0.61 | 0.66 |
| drug + experience type | 0.69 | 0.69 | 0.74 | 0.71 |
| all three | 0.79 | 0.74 | 0.77 | 0.74 |

The experience type says more about the rating than the drug in Birth Control, Depression and Acne. In Pain, knowing the drug says more, but adding the experience type still helps. Ratings are polarised: 35-44 % of the reviews are a 1 or a 10, and only 6-13 % are a 5 or 6.

## Where the results are

| File | For |
|---|---|
| `outputs/atc_agreement.csv` | Report: every test (condition × view × ATC level) |
| `outputs/profile_exceptions.csv` | Report: the exceptions and the side effects behind them |
| `outputs/rating_prediction.csv` | Report: AUC and balanced accuracy per condition and feature set |
| `outputs/drug_table.csv` | Everyone: the drugs, their class, number of reviews and mean rating |
| `outputs/drug_profiles_side_effects.csv`, `drug_profiles_experience_types.csv` | Everyone: the profiles |
| `outputs/drug_pair_similarity.csv` | Everyone: every pair of drugs, per view, with `same_class_level_4/3` |
| `outputs/cluster_rating_table.csv` | Report: mean rating per B cluster with C's label |
| `outputs/figures/` | Report: `drug_similarity_side_effects`, `drug_similarity_experience_types`, `atc_permutation_test`, `rating_prediction_auc` |
| `outputs/role_d_validation_run_stats.json` | Report: all numbers |

## How to run

Locally: run E's notebook first so that `../frequent_itemsets/outputs/baskets.parquet` exists (E needs A's clean data in `../frequent_itemsets/data/`), then **Restart & Run All** (about 1-2 minutes). On Kaggle: add B's, D's and E's notebook outputs as inputs (and C's dataset for the meaning view). All parameters are in section *0 · Setup and parameters*. Requires `numpy`, `pandas`, `pyarrow`, `scipy`, `scikit-learn` and `matplotlib`.

## Limitations

- ATC level 4 is a coarse yardstick for Depression (*N06AX*), and many Pain classes have a single drug.
- The profiles inherit the extractor's errors (precision 0.74, recall 0.67) and the drug-name effect of B's clusters.
- In Pain, *headache* is often the pain being treated, not a side effect.
- Some of B's clusters are opinions (*saved my life*), which helps the rating prediction.
- Reviews over-represent strong experiences. A profile describes what reviewers report, not true side-effect rates.

## To do

- [ ] Run it on Kaggle with C's masked embeddings to add the *meaning* view.
- [ ] Write the validation part of the report from `role_d_validation_run_stats.json` and the figures.
