# Data cleaning and LSH (Role A)

This notebook prepares the dataset that the rest of the group works with, and uses LSH (locality-sensitive hashing, the course topic *finding similar items*) to find similar reviews.

## Data

215,063 patient reviews of medicines from **Drugs.com** (UCI Drug Review Dataset, Drugs.com version; Kaggle mirror `jessicali9530/kuc-hackathon-winter-2018`). Each review has a drug, a condition, a rating from 1 to 10 and the review text.

## What the notebook does

1. **Cleans the text**: fixes broken symbols and repairs disease names that were cut off (for example "Bipolar Disorde" → "Bipolar Disorder").
2. **Removes exact copies**: the same review often appears twice, once under the brand name of a drug (*Zoloft*) and once under its generic name (*Sertraline*). 86,311 copies are removed.
3. **Removes near-copies with MinHash + LSH**: reviews that are almost identical. Our own implementation, which finds similar texts without comparing all 8.3 billion pairs. 87 near-copies are removed.
4. **Checks that LSH works**: compares LSH with a brute-force comparison of 305 million pairs and with 5,000 test pairs of known similarity. LSH finds all 165 real near-copies and is about 26 times faster than comparing every pair.
5. **Finds similar stories across drugs**: patients who describe the same experience with different medicines, found with LSH on the meaningful words of each review. The result is 1,711 shared stories and 93 drug pairs. A statistical test (permutation test) shows that 5 of these pairs share more stories than their condition alone explains.

**Main result:** 128,663 clean reviews with no copies, saved as `reviews_clean_deduplicated.parquet`.

## Where the results are

The output files (clean data, tables and figures) are in the **Output** tab of the Kaggle notebook:
https://www.kaggle.com/code/diegofogued/clean-and-deduplicate

| File | For |
|---|---|
| `reviews_clean_deduplicated.parquet` | Everyone: the clean data |
| `drug_family_story_similarity.csv` | Validation lead: drug pairs with similar stories and the test result (`is_significant`) |
| `drug_families.csv`, `brand_generic_drug_name_pairs.csv` | Validation lead: brand and generic names of the same medicine |
| `role_a_run_stats.json`, `lsh_setting_comparison.csv`, `lsh_recall_vs_theory.png` | Report: all numbers and the LSH figure |

## How to use the clean data in your own Kaggle notebook

1. In the right-hand panel, click **Add Input → Notebook Output** and search for **"Clean and deduplicate"**.
2. Load the file with this code:

```python
from pathlib import Path
import pandas as pd

path = next(Path('/kaggle/input').rglob('reviews_clean_deduplicated.parquet'))
reviews = pd.read_parquet(path)
```

3. For the review text, use the column `review_text_clean`. It keeps punctuation and negations such as "no weight gain".

## To do

- [ ] **Compare with the NLP lead's embeddings.** Repeat the similar-story search with the Sentence-BERT embeddings (LSH for cosine similarity with random hyperplanes), then compare it with the word version: which pairs both versions find, which only one finds, and examples of each.
- [ ] Agree with the validation lead on one name per drug (proposal: the generic name).
