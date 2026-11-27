# Role C · Sentence-BERT embeddings and automatic topic labels

This folder holds the NLP part: the new technique that was not taught in the course (Sentence-BERT embeddings and topic labelling).

## What it does

Embeds the 36,365 reviews of Birth Control, Depression, Pain and Acne with Sentence-BERT (`FremyCompany/BioLORD-2023`), describes Role B's 100 k-means clusters with keywords (c-TF-IDF written from scratch plus a KeyBERT-style selection), evaluates them with automatic metrics, and compares clustering by meaning with B's TF-IDF clusters, with and without drug names. The method and the code are explained step by step in the notebook.

## Contents

| Path | What it is |
|---|---|
| `nlp-embeddings.ipynb` | The whole analysis, step by step, documented, with its outputs |
| `outputs/` | Result files of the run in the notebook |
| `data/` | Role A's files (not committed; copy here or add on Kaggle). Role B's files are read from `../clustering/outputs` |

| File in `outputs/` | Contents |
|---|---|
| `cluster_labels_final.csv` | One row per cluster of B: keywords, label, mean rating, top drugs, NPMI, cohesion |
| `cluster_topics_ctfidf.csv` | c-TF-IDF terms per cluster and overlap with B's terms |
| `cluster_labels_sbert_auto.csv` | Five Sentence-BERT keywords per cluster |
| `cluster_coherence_metrics.csv` | NPMI, random baseline and cohesion per cluster |
| `sbert_vs_tfidf_summary.csv`, `sbert_masked_v2_summary.csv` | Clustering in meaning space, with and without drug names |
| `role_c_run_stats.json` | All numbers of the run |

## Notebook sections

| Section | What it does |
|---|---|
| C1 | Load A's data and B's clusters, keep the four conditions; C1b reloads the precomputed embeddings |
| C2–C3 | Sentence-BERT embeddings per condition; sanity check (rows, IDs, NaN, norm) |
| C4 | c-TF-IDF from scratch: the most distinctive terms of every cluster |
| C5 | KeyBERT-style keywords: similarity to the cluster centroid minus the condition centroid, with diversity (MMR) |
| C6–C7 | Cluster table; automatic metrics |
| C8 | Why only the k-means clusters are described (not DBSCAN) |
| C9 | k-means on the embeddings vs B's clusters, with and without drug names |
| C10 | Deliverables for A and D, run statistics |

## Large files (Kaggle dataset)

The embeddings are too large for GitHub (`embeddings_all.npy` is about 395 MB), so they are in a public Kaggle dataset:

**<https://www.kaggle.com/datasets/claudiagranado/dataset-input-versionantiguaresultados>**

It contains `embeddings_all.npy` + `embeddings_all_ids.parquet` (one 768-number vector for each of the 128,663 reviews, computed with `FremyCompany/BioLORD-2023`) and the masked version `embeddings_masked_v2_all.npy` + `embeddings_masked_v2_all_ids.parquet` (the 36,365 reviews of the four conditions, with drug names masked). They were computed once in an earlier Kaggle session with the code of section C2; the notebook reloads them from this dataset (C1b), so they are not computed again. The `embeddings_all.npy` that the notebook writes covers only the 36,365 reviews of the four conditions.

## How to run

1. Put Role A's files (`reviews_clean_deduplicated.parquet`, `drug_families.csv`, `brand_generic_drug_name_pairs.csv`) and Role B's files (`cluster_assignments.parquet`, `cluster_profiles.csv`) in `data/`, or add them as Kaggle datasets.
2. **Kaggle (recommended):** add those datasets and the embeddings dataset above as inputs, turn Internet on (the model is downloaded from Hugging Face) and run **Save & Run All**. It takes about 17 minutes. Seeds are fixed (`random_state=0`).
3. **To compute the embeddings from scratch:** run without the embeddings dataset and delete cell C1b (it needs the dataset). Sections C2 and C9 then encode the reviews, which takes hours on a CPU, so use a GPU. `EMBED_ALL_OTHER_REVIEWS = True` also embeds the other 92k reviews.
4. Kaggle deletes `/kaggle/working` when the session ends, so download the outputs before closing.

Requires: `numpy`, `pandas`, `scipy`, `scikit-learn`, `sentence-transformers`. All parameters are in section 0 of the notebook.

### Using the outputs in another notebook

```python
from pathlib import Path
import numpy as np
import pandas as pd

folder = next(p for p in [Path('/kaggle/input'), Path('../nlp-embeddings/outputs')] if p.exists())
E   = np.load(next(folder.rglob('embeddings_all.npy')))                    # (n_reviews, 768), length 1
ids = pd.read_parquet(next(folder.rglob('embeddings_all_ids.parquet')))    # same row = same review_id
vec = dict(zip(ids['review_id'], E))                                        # vec[review_id] -> 768 numbers
labels = pd.read_csv(next(folder.rglob('cluster_labels_final.csv')))        # one row per cluster of B
```

## Main results (this run, 100 clusters of B)

- **Topic terms:** c-TF-IDF overlaps 0.68 with B's top terms. In 51 of 100 clusters a drug or condition name is among the first five terms (14.3% of the top-10 terms on average).
- **Coherence:** mean NPMI of the cluster terms is 0.137 against −0.165 for random term sets. The mean cohesion gap is about 0 (−0.006): B's clusters are mostly not separated in meaning space.
- **Drug purity:** unmasked Sentence-BERT clusters are at least as drug-pure as B's (for example Depression 0.48 against 0.27, baseline 0.09); after masking drug names they fall below B's in three conditions and are close in Acne (0.31 against 0.32).
- **Agreement with B:** the ARI is between 0.03 and 0.16, so the two clusterings are different.
- **DBSCAN:** 11–26% noise and one giant cluster per condition.

## Limitations

- The keywords can only be terms that already appear in the c-TF-IDF candidates; they are suggestions, not final labels, and generic words, condition names and drug names slip in. This is measured, not filtered by hand.
- There is no manual labelling: the evaluation uses automatic metrics and a qualitative inspection of the keywords. The NPMI and cohesion evaluate the c-TF-IDF terms and B's clusters, not the Sentence-BERT keywords.
- One model only (BioLORD-2023, no model comparison); it reads at most 128 tokens, so longer reviews are truncated.
- The drug-name masking list is built only from project files and may miss some names. The share of names left after masking uses the same list, so it is not evidence that masking is complete.
- Number of candidates (30) and diversity (0.5) are design choices, not tuned on data.
