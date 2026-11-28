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
   unigrams to trigrams, `sublinear_tf=True`).
3. **B3 · Dimensionality reduction** — TruncatedSVD (300 components, LSA) + L2
   normalisation so Euclidean distance approximates cosine distance.
4. **B4 · K-means sweep** — sweep k = 2 … 26 per condition, plot Davies-Bouldin
   index and inertia elbow.  Result: k = 23 (Birth Control), 26 (Depression),
   26 (Pain), 25 (Acne).  **B4.1** explains the choice: DB keeps falling up to
   k = 50, so k is chosen by the elbow and by interpretability.
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
then **Restart & Run All** (about 15 minutes on a laptop).  All parameters are
in section *0 · Setup and parameters*.  Requires: `numpy`, `pandas`, `scipy`,
`scikit-learn`, `matplotlib` and `fastparquet` (the parquet engine used in B1).

**Reproducibility check (28 Nov).** A rerun from the raw UCI data gives the same
k in every condition, identical clusters in Birth Control and Acne, and 98–99.5 %
of the reviews in the same cluster in Depression and Pain (small numerical
differences between machines); the k-means DB values agree to 0.004.  DBSCAN
keeps the same parameters, but its number of clusters changes between runs in
Depression (3 vs 9) and Pain (4 vs 3), so the B6 table is the one of the
committed run.  Two cells at the start (a review reader imported from a local
`read_reviews.py` that is not in the repo) were removed so that the notebook runs
for everyone; B10 has the same review browser.

## Open points for the report

- **k:** say that the Davies-Bouldin index *kept falling in our data* up to
  k = 50, rather than that it always decreases (that is not a property of the
  index).  k = 23 for Birth Control is justified by interpretability (B4.1);
  the "consistency with the other roles" argument no longer holds, because the
  rerun with 300 components changed the clusters anyway.
- **DBSCAN:** B6 explains why its DB is not comparable (more than 97 % noise in
  Birth Control and Acne, DB computed only on the non-noise points).
- **Some clusters are a drug name** (*nexplanon*, *mirena*, *pristiq*): 26 of
  the 100 clusters have one drug with ≥ 50 % of their reviews.  The validation
  step leaves them out of the experience profiles.
- **t-SNE figure:** the title of `outputs/figures/tsne_clusters.png` still says
  150 LSA dimensions; the code now prints the real number (300), so the next run
  fixes the figure.

## To do

- [x] Label each cluster: C's automatic labels are in
  `../nlp-embeddings/outputs/cluster_labels_final.csv` (`label_final`).  They
  were made on the previous clustering (150 components): C has to rerun them
  on the current `cluster_assignments.parquet`.
- [x] Share `cluster_assignments.parquet` with C (NLP lead) for topic modelling
  and with D (validation) for the rating prediction step.
- [x] Decide how to justify k (B4.1).
- [ ] Write the Role B section of the report from `role_b_run_stats.json` and
  the figures.
