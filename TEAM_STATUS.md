# Team status: code and repository (25 Nov 2026)

For the team only: delete this file before submission.

## Where we are against the plan

| Gantt bar | Owner | Planned | State on 25 Nov |
|---|---|---|---|
| Clean + LSH dedup | A | Oct 28 - Nov 8 | ✅ Done, reproduces exactly. The saved notebook still lacks two steps (see A below) |
| ATC mapping | D | Oct 28 - Nov 8 | ✅ Done. Outputs re-saved from A's final data (same class for every review) |
| Side-effect baskets | E | Oct 28 - Nov 8 | ✅ Done, reproduces exactly |
| Vectorise + cluster | B | Nov 2 - Nov 15 | ✅ Runs and reproduces. One open decision on k (see B below) |
| PCY + association rules | E | Nov 9 - Nov 22 | ✅ Done |
| Embeddings + topics | C | Nov 9 - Nov 22 | ⚠️ Results exist, but the saved notebook is not one clean run |
| **Pipeline freeze** | All | **Nov 22** | ⚠️ Missed. Proposed new code freeze: **Nov 27** |
| Validation vs ATC | D | Nov 16 - **Nov 27** | ✅ Built (`validation/`), runs in ~1.5 min. Needs D's review |
| Figures | All | Nov 16 - Dec 1 | 🟡 Most figures are in each `outputs/figures/` folder; A's are only on Kaggle |
| Report writing | All | Nov 23 - Nov 29 | Not started |
| Full report draft | All | Nov 29 | |
| Review and polish | All | Nov 30 - Dec 3 | |
| Submission | All | Dec 4 | |

## What was fixed in this pass

- **New `validation/` stage** (RQ3 and RQ4): notebook, README and outputs. It is D's "Validation vs ATC" bar.
- **Top-level `README.md`**: pipeline, dependencies, data sources, how to run, reproducibility check.
- **`requirements.txt`** and **`run_pipeline.py`**: `python run_pipeline.py` rebuilds A → D → E → validation from the raw data in about 5 minutes (tested on a clean copy of the repo).
- **One local data layout**: the raw UCI files go in `data/raw/`. A also reads from there, and B, C and E also find A's outputs in `data-cleaning-and-lsh/outputs/`. These are one-line changes to each notebook's `INPUT_DIRS`; nothing changes on Kaggle.
- **A**: without `nltk`, A6 silently skipped stemming and found other stories (667 instead of 1,711). It now stops with a clear error.
- **C**: cell C1b worked only on Kaggle. It now finds the embeddings in any input folder and does nothing if they are missing, instead of crashing.
- **D**: outputs re-saved from A's final data (36,365 reviews in scope instead of 36,385; same class for every review). The README and its to-dos are updated.
- **E**: `baskets.parquet` and `drug_side_effect_profiles.csv` are now committed, because validation reads them; the rest of `outputs/` stays git-ignored. Also fixed a wrong path in the README.
- **B**: the README was out of date (k = 2-26 and 150 LSA components, not 2-12 and 100). It now lists the open points for the report.
- **`.gitignore`**: large files written by local runs (A's parquet files, C's `.npy` embeddings) are ignored.

## What we need from each person

Due dates follow the Gantt: the code must be final by the end of the validation bar (**Nov 27**), so that the figures (until Dec 1) and the report draft (Nov 29) use final numbers.

### A · Data and LSH lead (by Nov 27)
1. **One final Kaggle run of `clean-data-and-lsh.ipynb`** with D's `atc-mapping/outputs/drug_atc_mapping.csv` and C's embeddings dataset as inputs. The saved notebook has not run step A6 · 1b (canonical names) or A6b (search by meaning). The A6b numbers in the README (13,679 stories, 8 significant pairs) come from a run that is not in the notebook.
2. Commit the saved notebook and the **small outputs** (CSV, JSON and PNG, e.g. `lsh_recall_vs_theory.png`, `semantic_lsh_s_curve.png`, `role_a_run_stats.json`) to `data-cleaning-and-lsh/outputs/`. Today they are only on Kaggle, and the report needs them. The parquet files stay out (git-ignored).

### B · Clustering lead (decision by Nov 26)
1. **Decide how to justify k.** The Davies-Bouldin index keeps falling with k, so argmin(DB) ends at 23-26, the top of the sweep. Recommended: keep the current k (changing it means rerunning C and validation) and justify it in the report (elbow, interpretability), stating that DB alone does not settle k.
2. In the report, present the k-means vs DBSCAN comparison with its caveat: DBSCAN's DB is computed without its 11-26 % noise points, on only 2-3 clusters in three conditions.

### C · NLP lead (by Nov 27)
1. **One clean Restart & Run All on Kaggle** of `nlp-embeddings.ipynb`, with the embeddings dataset as input. Ten of its 17 code cells have outputs without an execution number, and some outputs are still in Spanish while the code is in English. Commit the notebook and `outputs/`.
2. **Run `validation/validation.ipynb` on Kaggle** with the embeddings dataset as input (plus B's, D's and E's outputs), so it adds the *meaning* view. Or agree with D to leave that view out.

### D · Validation lead (review by Nov 27)
1. **Review the validation notebook** (`validation/README.md` has the method and results). Choices to confirm:
   - drug = active ingredient + ATC class;
   - drugs with ≥ 50 reviews;
   - centred cosine similarity;
   - B's clusters where one drug has ≥ 50 % of the reviews are left out of the experience profiles;
   - ratings 5-6 are left out of the high/low prediction.
2. Check the re-saved ATC outputs (`atc-mapping/outputs/`, made from A's final data).

### E · Frequent-itemset lead (by Nov 28)
1. Confirm that `baskets.parquet` and `drug_side_effect_profiles.csv` can stay committed.
2. Recommended: **check a sample of baskets by hand**, e.g. 50 reviews. The precision 0.74 and recall 0.67 come from LLM-made labels, and the project plan promises a check by hand. A human check makes these numbers defensible in the report.

### Everyone
1. **Push this pass to GitHub today.** This copy is a zip download, not a git clone. The changed and new files are listed below.
2. **Decide the appendix format by Nov 27.** The brief asks for "a Jupyter Notebook". Options: (a) submit the six notebooks with the README and `run_pipeline.py`; (b) add one short main notebook that explains the pipeline and links the six.
3. **Final rerun on Nov 28**, after A's and C's Kaggle runs: `python run_pipeline.py` locally, then check that every README's numbers still match its `outputs/`.
4. Write the contribution table for the report appendix from the team split in the project plan.

## Files changed or added in this pass

| File | Change |
|---|---|
| `README.md`, `TEAM_STATUS.md`, `requirements.txt`, `run_pipeline.py` | New or rewritten |
| `.gitignore` | Commits E's two downstream tables; ignores large local files |
| `validation/` (notebook, README, outputs) | New |
| `data-cleaning-and-lsh/clean-data-and-lsh.ipynb` | `INPUT_DIRS` also reads `../data/raw`; `nltk` is required (2 cells, outputs unchanged) |
| `data-cleaning-and-lsh/README.md` | Reproducibility check, to-dos |
| `nlp-embeddings/nlp-embeddings.ipynb` | `INPUT_DIRS` also reads A's local outputs; cell C1b works outside Kaggle (2 cells, outputs unchanged) |
| `nlp-embeddings/README.md` | State of the notebook, how to run, to-dos |
| `clustering/clustering.ipynb` | `INPUT_DIRS` also reads A's local outputs (1 line) |
| `clustering/README.md` | Correct parameters, reproducibility, open points |
| `frequent_itemsets/frequent-itemsets.ipynb` | `INPUT_DIRS` also reads A's local outputs (1 line) |
| `frequent_itemsets/README.md` | Path fix, requirements, reproducibility, to-dos |
| `frequent_itemsets/outputs/baskets.parquet`, `drug_side_effect_profiles.csv` | Now committed |
| `atc-mapping/atc-mapping.ipynb`, `atc-mapping/outputs/*` | Re-run on A's final data |
| `atc-mapping/README.md` | Input, numbers, to-dos |

Not to commit: `data/raw/` (raw data), `frequent_itemsets/data/` (a local copy of A's clean data). Both are git-ignored.
