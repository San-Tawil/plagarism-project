# READ DOCUMENTS MODULE

import os


def _read_text_with_fallbacks(file_path):
    encodings = ("utf-8", "utf-8-sig", "latin-1", "cp1252")
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    return ""


def load_documents_from_folder(folder_path):
    document_list = []
    document_id = 0

    file_names = sorted(os.listdir(folder_path))
    for file_name in file_names:
        if file_name.endswith(".txt"):
            full_path = os.path.join(folder_path, file_name)
            file_content = _read_text_with_fallbacks(full_path)
            if not file_content.strip():
                continue

            document_list.append({
                "doc_id":   document_id,
                "doc_name": file_name,
                "doc_text": file_content
            })
            document_id += 1

    return document_list


"""
READ DOCUMENTS NOTES

PURPOSE:
    Loads all .txt files from a given folder into memory for downstream processing.
    Each document is stored as a dictionary with a unique numeric ID, the file name,
    and the raw text content.

FUNCTION: load_documents_from_folder(folder_path)

Parameters:
    folder_path (str) : path to the folder containing .txt documents

Returns:
    list of dicts, each with keys:
        "doc_id"   -> unique integer ID assigned in loading order
        "doc_name" -> original file name (e.g. "doc1.txt")
        "doc_text" -> full raw text content of the file

Steps:
    1. Scan the folder with os.listdir()
    2. Filter files by ".txt" extension
    3. Open each file with UTF-8 encoding
    4. Append a structured dict to document_list
    5. Increment doc_id for each file

TIME COMPLEXITY:

    Let n = number of .txt files in the folder
    Let L = average character length of each document

    Reading all files: O(n * L)
    Each character is read exactly once per file.

    Total: O(n * L)

SPACE COMPLEXITY:

    O(n * L)

    The full text of every document is stored in memory.
    This is necessary because preprocessing and hashing happen later
    as separate steps, not during file reading.

DESIGN CHOICES:

    - os.listdir() is used to scan the folder (allowed by the project spec).
    - Only .txt files are accepted; other file types are silently skipped.
    - doc_id is assigned as a simple incrementing integer for lightweight indexing.
    - UTF-8 encoding is specified explicitly to avoid encoding errors on
      systems where the default encoding differs.
    - The function returns a flat list so that the caller (main.py) controls
      iteration order and downstream steps.

KEY NAMING CONVENTION:

    "doc_id"   -> used throughout the pipeline to identify documents
    "doc_name" -> kept for display purposes only
    "doc_text" -> raw text passed to the preprocessing module

    All downstream modules (preprocessing, hashing, similarity) reference
    these exact keys to maintain consistency.


"""
