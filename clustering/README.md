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
3. **B3 · Dimensionality reduction** — TruncatedSVD (100 components, LSA) + L2
   normalisation so Euclidean distance approximates cosine distance.
4. **B4 · K-means sweep** — sweep k = 2 … 12 per condition, plot Davies-Bouldin
   index and inertia elbow, pick k_best = argmin(DB).
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
then **Restart & Run All** (about 3–5 minutes).  All parameters are in
section *0 · Setup and parameters*.  Requires: `numpy`, `pandas`, `scipy`,
`scikit-learn`, `matplotlib`.

## To do

- [ ] Label each cluster with a short name after inspecting the top terms and
  sample reviews (target names: "weight gain", "mood swings", "worked fast,
  no side effects", "stopped because of nausea").
- [ ] Share `cluster_assignments.parquet` with C (NLP lead) for topic modelling
  and with D (validation) for the rating prediction step.
- [ ] Write the Role B section of the report from `role_b_run_stats.json` and
  the figures.
