import importlib.util
import os
import sys

from Read_Documents import load_documents_from_folder
from Preproccessing_documents import preprocess_document_text
from hashing import build_table_chaining, build_table_double
from Jaccard import compute_all_similarity_scores
from divide_and_conquer import compute_all_divide_conquer_scores
from Red_black_trees import RedBlackTree
from display import (
    display_loading,
    display_preprocessing,
    display_hash_stats,
    compare_hash_tables,
    display_results,
    display_summary,
    display_rbt_inorder,
    display_rbt_high_range,
)

# Make terminal output robust on Windows code pages.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _load_merge_sort_similarity():
    """
    Reuse an existing merge-sort implementation if available.
    """
    try:
        from Sorting import merge_sort_similarity as sorter
        return sorter
    except Exception:
        pass

    lab_sorting_path = os.path.join(
        os.path.dirname(__file__),
        "cp3 project lab",
        "Sorting.py",
    )
    spec = importlib.util.spec_from_file_location("lab_sorting", lab_sorting_path)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load merge_sort_similarity from Sorting modules.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.merge_sort_similarity


def run_pipeline(folder_path):
    # STEP 1: LOAD DOCUMENTS
    docs = load_documents_from_folder(folder_path)
    if len(docs) == 0:
        print("No .txt files found in folder:", folder_path)
        return

    docs_for_loading_display = []
    i = 0
    while i < len(docs):
        doc = docs[i]
        docs_for_loading_display.append((str(doc["doc_id"]), doc["doc_text"].split()))
        i += 1
    display_loading(docs_for_loading_display)

    # STEP 2: PREPROCESS + BUILD TABLES + STORE TOKENS
    display_preprocessing()

    doc_tables_chain = []
    doc_tables_double = []
    doc_tokens = []

    i = 0
    while i < len(docs):
        doc = docs[i]
        doc_id = doc["doc_id"]
        tokens = preprocess_document_text(doc["doc_text"])

        ht_chain = build_table_chaining(tokens)
        ht_double = build_table_double(tokens)

        doc_tables_chain.append((doc_id, ht_chain))
        doc_tables_double.append((doc_id, ht_double))
        doc_tokens.append((doc_id, tokens))
        i += 1

    # STEP 3: HASH TABLE REPORTS
    display_hash_stats(doc_tables_chain, doc_tables_double)
    compare_hash_tables(doc_tables_chain, doc_tables_double)

    merge_sort_similarity = _load_merge_sort_similarity()

    def _format_results_for_display(results):
        formatted = []
        idx = 0
        while idx < len(results):
            doc1_id, doc2_id, score = results[idx]
            formatted.append((str(doc1_id), str(doc2_id), score))
            idx += 1
        return formatted

    def _build_rbt_from_results(results):
        tree = RedBlackTree()
        idx = 0
        while idx < len(results):
            doc1_id, doc2_id, score = results[idx]
            tree.insert({
                "doc1": str(doc1_id),
                "doc2": str(doc2_id),
                "similarity": score
            })
            idx += 1
        return tree

    # STEP 4: JACCARD (existing, unchanged)
    print("\n JACCARD (MAIN METHOD)")
    jaccard_results = compute_all_similarity_scores(doc_tables_chain)
    merge_sort_similarity(jaccard_results)
    jaccard_display = _format_results_for_display(jaccard_results)
    display_results(jaccard_display)
    display_summary(jaccard_display)
    jaccard_tree = _build_rbt_from_results(jaccard_results)
    display_rbt_inorder("JACCARD", jaccard_tree.inorder_list())
    display_rbt_high_range("JACCARD", jaccard_tree.range_query_list(0.8, 1.0), 0.8, 1.0)

    # STEP 5: DIVIDE-AND-CONQUER POSITIONAL SIMILARITY (additional)
    print("\n DIVIDE-AND-CONQUER POSITIONAL ")
    dac_results = compute_all_divide_conquer_scores(doc_tokens)
    merge_sort_similarity(dac_results)
    dac_display = _format_results_for_display(dac_results)
    display_results(dac_display)
    display_summary(dac_display)
    dac_tree = _build_rbt_from_results(dac_results)
    display_rbt_inorder("DIVIDE-AND-CONQUER", dac_tree.inorder_list())
    display_rbt_high_range("DIVIDE-AND-CONQUER", dac_tree.range_query_list(0.8, 1.0), 0.8, 1.0)


if __name__ == "__main__":
    documents_folder = "documents"

    if not os.path.exists(documents_folder):
        print("Error: folder '" + documents_folder + "' not found.")
        print("Create a folder named 'documents' next to main.py and add .txt files to it.")
    else:
        run_pipeline(documents_folder)

