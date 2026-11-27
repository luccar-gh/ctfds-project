# Clustering (Role B)

This notebook vectorises every patient review in the four scope conditions and
clusters them with **k-means** and **DBSCAN**, choosing *k* by minimising the
**Davies-Bouldin index**.  It answers research question 1: *Can patient reviews
be grouped into common experience types?*

## Data

Role A's output: `reviews_clean_deduplicated.parquet` (128,663 clean reviews)
and `drug_families.csv`.  We use the 36,365 reviews of the four conditions:
**Birth Control, Depression, Pain and Acne**.

## What the notebook does

1. **B1 · Load and scope** — load Role A's clean data, keep the four conditions.
2. **B2 · TF-IDF vectorisation** — one vectoriser per condition (20k features,
   bigrams, `sublinear_tf=True`).
3. **B3 · Dimensionality reduction** — TruncatedSVD (150 components, LSA) + L2
   normalisation so Euclidean distance approximates cosine distance.
4. **B4 · K-means sweep** — sweep k = 2 … 26 per condition, plot Davies-Bouldin
   index and inertia elbow, pick k_best = argmin(DB).  Result: k = 23 (Birth
   Control), 26 (Depression), 26 (Pain), 25 (Acne).
5. **B5 · DBSCAN** — kNN distance plot to choose eps, then grid search over
   eps × min_samples; score valid configs with Davies-Bouldin.
6. **B6 · Compare** — side-by-side DB scores for k-means vs DBSCAN.
7. **B7 · Cluster profiles** — top-10 TF-IDF terms per cluster, mean rating,
   sample reviews, heatmap of term weights, 2D scatter plot.
8. **B8 · Rating vs cluster** — Kruskal-Wallis test: does cluster membership
   predict rating?  Boxplot per condition.
9. **B9 · Save outputs** — parquet, CSV and JSON for the report.

## What is in this folder

| Path | What it is |
|---|---|
| `clustering.ipynb` | The whole analysis, step by step |
| `data/` | Role A's files (not committed — copy here or add on Kaggle) |
| `outputs/` | Created by the notebook |

## Where the results are

| File | For |
|---|---|
| `outputs/cluster_assignments.parquet` | Everyone: join to any table on `review_id` |
| `outputs/cluster_profiles.csv` | Report: top terms and mean rating per cluster |
| `outputs/figures/` | Report: `kmeans_sweep`, `dbscan_knn_distances`, `kmeans_scatter`, `cluster_terms_*`, `rating_by_cluster` |
| `outputs/role_b_run_stats.json` | Report: all numbers (k_best, DB scores, Kruskal-Wallis) |

## How to use the cluster assignments in your own notebook

```python
from pathlib import Path
import pandas as pd

folder = next(p for p in [Path('/kaggle/input'), Path('../clustering/outputs')] if p.exists())
clusters = pd.read_parquet(next(folder.rglob('cluster_assignments.parquet')))
```

Columns: `review_id`, `condition_name`, `drug_family`, `rating`,
`kmeans_cluster`, `dbscan_cluster`.  Join on `review_id`.

## How to run

Put Role A's two files in `data/` (or add A's notebook output on Kaggle),
then **Restart & Run All** (about 3–6 minutes).  All parameters are in
section *0 · Setup and parameters*.  Requires: `numpy`, `pandas`, `scipy`,
`scikit-learn`, `matplotlib` and `fastparquet` (the parquet engine used in B1).

**Reproducibility check (25 Nov).** A rerun from the raw UCI data gives the same
k in every condition, identical clusters in Birth Control and 95–99 % of reviews
in the same cluster in the other three (small numerical differences between
machines).  The chosen DBSCAN `min_samples` changed in Depression and Acne.
The committed outputs are the ones C's labels and the validation step use, so
they were not replaced.

## Open points for the report

- **k is at the edge of the sweep.**  The Davies-Bouldin index keeps falling as
  k grows, so argmin(DB) lands at 23–26, the top of the range (the range was
  already extended once from 20).  The report has to justify k another way
  (elbow, interpretability, or a cap) or say that DB alone does not settle it.
- **DBSCAN's lower DB is not a fair comparison.**  DB is computed without the
  noise points (11–26 % of the reviews), and DBSCAN finds only 2–3 clusters in
  three conditions.
- **Some clusters are a drug name** (*nexplanon*, *mirena*, *pristiq*): 27 of
  the 100 clusters have one drug with ≥ 50 % of their reviews.  The validation
  step leaves them out of the experience profiles.

## To do

- [x] Label each cluster: C's automatic labels are in
  `../nlp-embeddings/outputs/cluster_labels_final.csv` (`label_final`).
- [x] Share `cluster_assignments.parquet` with C (NLP lead) for topic modelling
  and with D (validation) for the rating prediction step.
- [ ] Decide how to justify k (see *Open points*).
- [ ] Write the Role B section of the report from `role_b_run_stats.json` and
  the figures.
