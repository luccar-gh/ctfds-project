"""Run the project's notebooks in order on a local machine and save each one with its outputs.

    python run_pipeline.py                    # A, D, E and validation: about 5 minutes on a laptop
    python run_pipeline.py --with-clustering  # also B (clustering, about 5 more minutes), see the note below
    python run_pipeline.py E V                # only some stages, in pipeline order

Before the first run: pip install -r requirements.txt, and put the raw UCI files
drugsComTrain_raw.tsv and drugsComTest_raw.tsv in data/raw/ (see README.md).

Why B and C are not in the default run:
- B: a rerun gives the same k but moves 1-5 % of the reviews to another cluster in three conditions
  (numerical differences between machines). C's cluster labels and the committed results are built on
  the committed clusters, so B is only rerun on request.
- C: computing the Sentence-BERT embeddings needs a GPU (or hours on a CPU). Run it on Kaggle with the
  embeddings dataset as input (see nlp-embeddings/README.md); --with-nlp runs it here anyway.
"""
import argparse
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent
STAGES = {   # pipeline order: every stage only reads the outputs of the stages before it
    'A': ('Clean + LSH dedup', 'data-cleaning-and-lsh/clean-data-and-lsh.ipynb'),
    'D': ('ATC mapping', 'atc-mapping/atc-mapping.ipynb'),
    'B': ('Vectorise + cluster', 'clustering/clustering.ipynb'),
    'E': ('Side-effect baskets, PCY + rules', 'frequent_itemsets/frequent-itemsets.ipynb'),
    'C': ('Embeddings + topics', 'nlp-embeddings/nlp-embeddings.ipynb'),
    'V': ('Validation vs ATC, rating prediction', 'validation/validation.ipynb'),
}
DEFAULT_STAGES = ['A', 'D', 'E', 'V']
RAW_FILES = ['drugsComTrain_raw', 'drugsComTest_raw']


def raw_data_found():
    folders = [ROOT / 'data' / 'raw', ROOT / 'data-cleaning-and-lsh' / 'data' / 'raw']
    return all(any(folder.glob(stem + ext) for folder in folders if folder.exists() for ext in ('.tsv', '.csv'))
               for stem in RAW_FILES)


def run_notebook(path):
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=7200, kernel_name='python3',
                            resources={'metadata': {'path': str(path.parent)}})
    try:
        client.execute()
    finally:
        nbformat.write(notebook, path)   # saved with its outputs, also when a cell fails


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stages', nargs='*', help=f'stages to run, from {list(STAGES)} (default: {DEFAULT_STAGES})')
    parser.add_argument('--with-clustering', action='store_true', help='also rerun B')
    parser.add_argument('--with-nlp', action='store_true', help='also rerun C (needs a GPU or the embeddings dataset)')
    args = parser.parse_args()

    chosen = set(args.stages or DEFAULT_STAGES)
    if args.with_clustering:
        chosen.add('B')
    if args.with_nlp:
        chosen.add('C')
    unknown = chosen - set(STAGES)
    if unknown:
        parser.error(f'unknown stages {sorted(unknown)}; choose from {list(STAGES)}')
    if 'A' in chosen and not raw_data_found():
        sys.exit('The raw UCI files are missing: put drugsComTrain_raw.tsv and drugsComTest_raw.tsv in data/raw/ '
                 '(download: https://archive.ics.uci.edu/ml/machine-learning-databases/00462/drugsCom_raw.zip)')

    started = time.perf_counter()
    for key in [key for key in STAGES if key in chosen]:
        name, notebook = STAGES[key]
        print(f'[{key}] {name}: running {notebook} ...', flush=True)
        stage_started = time.perf_counter()
        run_notebook(ROOT / notebook)
        print(f'[{key}] done in {time.perf_counter() - stage_started:.0f} s', flush=True)
    print(f'All done in {(time.perf_counter() - started) / 60:.1f} minutes')


if __name__ == '__main__':
    main()
