# Document Similarity Engine (CSC310)

This project is a Python command-line application that compares `.txt` documents inside the `documents/` folder.

It implements:
- custom hash tables (separate chaining and double hashing),
- pairwise Jaccard similarity,
- divide-and-conquer positional similarity,
- sorting and reporting of similarity results,
- red-black tree storage and range queries for similarity scores.

## Requirements

- Python 3.9+
- Standard library only (for `main.py`)
- For the Streamlit UI: `streamlit`, `pandas`, `plotly`

## Project Structure

- `main.py` - entry point and pipeline orchestration
- `Read_Documents.py` - loads `.txt` files from a folder
- `Preproccessing_documents.py` - text preprocessing (lowercase, punctuation handling, tokenization)
- `hashing.py` - custom hash-table implementations and builders
- `Jaccard.py` - Jaccard similarity across document pairs
- `divide_and_conquer.py` - recursive positional similarity
- `Red_black_trees.py` - red-black tree for sorted/range views of similarity
- `display.py` - terminal output formatting
- `documents/` - input text files used by the pipeline

## How To Run

### Command Line Interface
From the project root:

```bash
python main.py
```

### Streamlit Web UI
To run the interactive web interface:

```bash
streamlit run streamlit_app.py
```

## Expected Input

- A folder named `documents` must exist next to `main.py`.
- The folder should contain one or more `.txt` files.
- Files are read as UTF-8.

If the folder is missing, the program prints:
- an error message,
- and instructions to create `documents/`.

If the folder exists but has no `.txt` files, the run exits early with a notice.

## Pipeline Overview

1. Load documents from `documents/`.
2. Preprocess each document into tokens.
3. Build two hash tables per document (chaining and double hashing).
4. Display hash-table stats and collision comparison.
5. Compute and rank pairwise **Jaccard** similarity.
6. Compute and rank pairwise **divide-and-conquer positional** similarity.
7. Insert each result set into a **red-black tree**.
8. Display:
   - sorted similarity results,
   - summary statistics,
   - inorder red-black tree output,
   - high-similarity range query output (`0.8` to `1.0`).

## Output Sections

During execution, the terminal shows:
- loaded document counts,
- preprocessing status,
- hash table statistics,
- collision comparison,
- Jaccard similarity report and summary,
- divide-and-conquer similarity report and summary,
- red-black tree inorder and range outputs for both methods.

## Notes

- This repository also contains a `cp3 project lab/` subfolder with another project copy and its own README.
- The root pipeline described here is based on the root `main.py` and modules listed above.
