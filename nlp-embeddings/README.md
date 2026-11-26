# NLP embeddings and topic labels (Role C)

This notebook turns every review into a vector that captures its **meaning** (Sentence-BERT, the new technique that was not taught in the course). The vectors are used to compare clustering in meaning space with B's TF-IDF clusters (Davies-Bouldin index), to describe B's clusters (class-based TF-IDF written from scratch plus embedding similarity), and as input for A's meaning version of the similar-story search.

## Data

Role A's `reviews_clean_deduplicated.parquet` (128,663 clean reviews), `drug_families.csv` and `brand_generic_drug_name_pairs.csv`, and Role B's `cluster_assignments.parquet` and `cluster_profiles.csv` (k-means clusters of Birth Control, Depression, Pain and Acne: 23, 26, 26 and 25 clusters, 100 in total; 36,365 reviews).

## What the notebook does

1. **C1 · Load and scope**: load A's and B's files, keep the four conditions, and reload the embeddings computed in an earlier Kaggle session (see "Large files").
2. **C2 · Sentence-BERT embeddings**: `FremyCompany/BioLORD-2023` (biomedical) gives 768 numbers per review (length 1, so the dot product is the cosine similarity). Optionally also for the 92k reviews of the other conditions.
3. **C3 · Sanity check**: rows, `review_id`s, NaN and vector length agree.
4. **C4 · Topic terms from scratch**: class-based TF-IDF (the idea behind BERTopic), written with numpy. Each cluster is one big document; terms that are frequent in the cluster and rare in the others score high. Compared with B's terms.
5. **C5 · Topic keywords (KeyBERT-style)**: the 30 c-TF-IDF candidates of each cluster are embedded and ranked by cosine similarity to the cluster centroid minus the similarity to the centroid of the whole condition (so that terms describing the whole condition lose out to terms specific to the cluster), with a diversity penalty (MMR) so that the five chosen terms are not variants of one word. No hand-written list.
6. **C6 · Cluster table**: reviews, mean rating and top drugs of each of B's 100 clusters.
7. **C7 · Automatic validation**: NPMI coherence of each cluster's top terms against a random-word baseline, and embedding cohesion. No manual labelling.
8. **C8 · DBSCAN**: why only the k-means clusters are described (11–26% noise, and one giant cluster plus micro-clusters in every condition).
9. **C9 · Clustering in meaning space**: k-means on the embeddings with B's k, with and without drug names (replaced by "medication"). Davies-Bouldin, drug purity, ARI vs B and rating spread.
10. **C10 · Save outputs**: embeddings for A, labels for D, statistics for the report.

## What is in this folder

| Path | What it is |
|---|---|
| `nlp-embeddings.ipynb` | The whole analysis, step by step |
| `data/` | Role A's files (not committed — copy here or add on Kaggle); B's files are read from `../clustering/outputs` |
| `outputs/` | Created by the notebook |

## Where the results are

| File | For |
|---|---|
| `outputs/embeddings_all.npy` + `embeddings_all_ids.parquet` | **A**: one vector (768) per `review_id`. The file written by the notebook covers the 36,365 reviews of the four conditions; the full 128,663-review file is in the [Kaggle dataset](https://www.kaggle.com/datasets/claudiagranado/dataset-input-versionantiguaresultados) (about 395 MB, so it is not on GitHub) |
| `outputs/cluster_labels_final.csv` | **D** and report: one row per k-means cluster (keywords, label, metrics) |
| `outputs/cluster_topics_ctfidf.csv`, `cluster_labels_sbert_auto.csv`, `cluster_coherence_metrics.csv` | Report: c-TF-IDF terms, Sentence-BERT keywords and quality metrics per cluster |
| `outputs/sbert_vs_tfidf_summary.csv`, `sbert_masked_v2_summary.csv` | Report: clustering in meaning space (with and without drug names) |
| `outputs/role_c_run_stats.json` | Report: all numbers |

## Large files (Kaggle dataset)

The embeddings are too large for GitHub (`embeddings_all.npy` is about 395 MB), so they are in a Kaggle dataset:

**<https://www.kaggle.com/datasets/claudiagranado/dataset-input-versionantiguaresultados>**

It contains `embeddings_all.npy` + `embeddings_all_ids.parquet` (one 768-number vector for each of the 128,663 reviews, computed with `FremyCompany/BioLORD-2023`) and the masked version `embeddings_masked_v2_all.npy` + `embeddings_masked_v2_all_ids.parquet` (the 36,365 reviews of the four conditions, with drug names masked).

**For A:** these are the files needed for the similar-story search by meaning. In Kaggle, use *Add Input → Datasets* and search for `dataset-input-versionantiguaresultados`; the code in the next section loads them. The vectors do not depend on B's clusters, so they stay valid when B changes `k`.

**Role C's notebook uses this dataset as an input:** it rebuilds the per-condition embedding files from it, so the embeddings are not computed again, and it writes its results, such as `cluster_labels_final.csv`, to `outputs/`, which are in this folder.

## How to use the embeddings and labels in your own notebook

```python
from pathlib import Path
import numpy as np
import pandas as pd

folder = next(p for p in [Path('/kaggle/input'), Path('../nlp-embeddings/outputs')] if p.exists())
E   = np.load(next(folder.rglob('embeddings_all.npy')))                    # (n_reviews, 768), length 1
ids = pd.read_parquet(next(folder.rglob('embeddings_all_ids.parquet')))    # same row = same review_id
vec = dict(zip(ids['review_id'], E))                                        # vec[review_id] -> 768 numbers
labels = pd.read_csv(next(folder.rglob('cluster_labels_final.csv')))        # condition, cluster, n_reviews, mean_rating, top_drugs, sbert_keywords, ctfidf_top5, npmi, cohesion_gap, label_final, label_source, b_top_terms
```

## How to run

Put Role A's and B's files in `data/` (or add them as a Kaggle dataset), then **Restart & Run All**. BioLORD is several times slower than small models: use a GPU (Kaggle or Colab). To avoid recomputing, add the Kaggle dataset above as an input; the notebook rebuilds the per-condition files from it. To compute the embeddings from scratch, run without that dataset and delete the cell C1b (it needs the dataset); C2 and C9 then compute the embeddings. `EMBED_ALL_OTHER_REVIEWS = True` also embeds the other 92k reviews (this is how the dataset above was created). Later runs reuse the saved `.npy` files. Kaggle deletes `/kaggle/working` when the session ends, so download the outputs (or save them as a dataset) before closing. Embeddings do not depend on B's clusters, so they can be reused if B changes `k`: only C1 and C4 onwards need to be re-run. Requires: `numpy`, `pandas`, `scipy`, `scikit-learn`, `sentence-transformers`.

## Main results (this run, 100 clusters of B)

- **Topic terms:** c-TF-IDF overlaps 0.68 with B's top terms. In 51 of 100 clusters a drug or condition name is among the first five terms.
- **Coherence:** mean NPMI of the cluster terms is 0.137 against -0.165 for random term sets. The mean cohesion gap is about 0 (-0.006): B's clusters are mostly not separated in meaning space.
- **Drug purity:** unmasked Sentence-BERT clusters are at least as drug-pure as B's (for example Depression 0.48 against 0.27, baseline 0.09); after masking drug names they fall below B's in three conditions (Depression 0.14, Birth Control 0.26, Pain 0.15) and are close in Acne (0.31 against 0.32).
- **Agreement with B:** the ARI is between 0.03 and 0.16, so the two clusterings are different.
- **DBSCAN:** 11–26% noise and one giant cluster per condition.

## Limitations

- The Sentence-BERT keywords can only be terms that already appear in the c-TF-IDF candidates; they are suggestions, not final labels.
- One model only (BioLORD-2023), chosen for domain fit; no model comparison is run in this notebook. The model reads at most 128 tokens (`max_seq_length`), so longer reviews are truncated.
- Embeddings group partly by drug name; masking reduces this, but the masking list is built only from project data and may miss some brands, so results depend on it. The share of reviews with a name left after masking is computed with the same list, so it is not evidence that masking is complete.
- With BioLORD, cosine similarities are higher than with MiniLM in general: a cosine threshold (for A's LSH, for example) should be chosen from the distribution, not copied from a typical value.
- There is no manual labelling: `label_final` is made of the first three Sentence-BERT keywords, not a sentence written by a person. The evaluation uses automatic metrics (NPMI against a random baseline, cohesion, Davies-Bouldin, drug purity, ARI) and a qualitative inspection of the keywords.
- The automatic metrics of C7 evaluate the c-TF-IDF terms and B's clusters, not the Sentence-BERT keywords.

## To do

- [x] Give A the full `embeddings_all.npy` (128,663 reviews) through the Kaggle dataset linked above; A implements the cosine LSH and the comparison with the word version.
- [x] Agree with D which clustering to use (k-means of B, 100 clusters) and share `cluster_labels_final.csv`: the validation step uses both.
- [x] One clean *Save & Run All* on Kaggle with the embeddings dataset as input (about 17 min); `nlp-embeddings.ipynb` in this folder is that run, with its outputs, and `outputs/` holds its files.
- [ ] Run the validation notebook on Kaggle with the embeddings dataset as input, to add its *meaning* view.
- [ ] Write the Role C section of the report from `role_c_run_stats.json`.

## Note on topic keywords

Generic words (*doctor, medication, went*), condition names and drug names appear among the keywords. They are **not** filtered with a hand-written list (any such list would be arbitrary); instead C4 measures the share of terms that are drug or condition names (`share_name_terms_top10`, 0.143 on average) and this is reported as a finding and limitation. There is no manual labelling step: the evaluation uses the automatic metrics in C7 and C9.

Subtracting the similarity to the condition centroid removed the condition name from the keywords (for example "depression" in many depression clusters) and brought up more specific terms (for example "suicidal thoughts", "panic attacks", "degenerative disc"), but it also let more filler words through (for example "time", "years", "really"). The keywords are therefore a suggestion that is useful mostly in their first positions. The automatic metrics of C7 evaluate the c-TF-IDF terms and the clusters, not these keywords.
