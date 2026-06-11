# JACCARD SIMILARITY MODULE


def jaccard_similarity(ht1, ht2):
    """
    Compute Jaccard similarity between two documents represented as hash tables.

    Formula:  J(A, B) = |A ∩ B| / |A ∪ B|

    where:
        A ∩ B  = number of unique words that appear in BOTH documents
        A ∪ B  = total number of unique words across BOTH documents
                 = |A| + |B| - |A ∩ B|

    Parameters:
        ht1 : HashTableChaining or HashTableDouble for document 1
        ht2 : HashTableChaining or HashTableDouble for document 2

    Returns:
        float in [0.0, 1.0]
        0.0 = no words in common
        1.0 = identical word sets
    """

    # --- compute intersection ---
    # iterate every unique word in document 1;
    # if it also exists in document 2, count it
    keys1        = ht1.keys_list()
    intersection = 0

    i = 0
    while i < len(keys1):
        if ht2.get(keys1[i]) > 0:
            intersection += 1
        i += 1

    # --- compute union ---
    # |A ∪ B| = |A| + |B| - |A ∩ B|
    # ht.count holds the number of unique keys stored in the table
    union = ht1.count + ht2.count - intersection

    if union == 0:
        return 0.0

    return intersection / union


def compute_all_similarity_scores(doc_tables):
    """
    Compute pairwise Jaccard similarity for every combination of documents.

    Parameters:
        doc_tables : list of (doc_id, hash_table) tuples
                     one entry per document, using chaining tables

    Returns:
        list of (doc_id_1, doc_id_2, score) tuples
        unsorted; caller should pass to merge_sort_similarity()
    """

    similarity_results = []
    total              = len(doc_tables)

    i = 0
    while i < total:
        j = i + 1
        while j < total:
            doc1_id, ht1 = doc_tables[i]
            doc2_id, ht2 = doc_tables[j]

            score = jaccard_similarity(ht1, ht2)
            similarity_results.append((doc1_id, doc2_id, score))

            j += 1
        i += 1

    return similarity_results


"""
JACCARD SIMILARITY NOTES

PURPOSE:
    Measures how similar two documents are by comparing their unique word sets.
    Uses the custom hash tables from hashing.py — no Python set or dict is used.

FORMULA

    J(A, B) = |A ∩ B| / |A ∪ B|

    Worked example (by hand):

        Document 1 words: { data, structures, algorithms, hash }
        Document 2 words: { data, algorithms, design, hash }

        Intersection = { data, algorithms, hash }  -> size = 3
        Union        = { data, structures, algorithms, hash, design } -> size = 5

        J = 3 / 5 = 0.6

    Score range:
        0.0  -> no overlap at all
        1.0  -> identical word sets

HOW INTERSECTION IS COMPUTED WITHOUT PYTHON SET

    keys_list() on ht1 returns every unique word stored in document 1's table.
    For each word, ht2.get(word) is called. If the return value > 0,
    the word exists in document 2. This is a pure hash table lookup — O(1) avg.

    This replaces the forbidden  `set1 & set2`  operation.

HOW UNION IS COMPUTED

    |A ∪ B| = |A| + |B| - |A ∩ B|

    ht.count stores the number of unique keys in the table.
    This is incremented only on first insertion of each key in hashing.py,
    so it correctly represents |A| and |B| (unique word counts).

    This replaces the forbidden  `set1 | set2`  operation.

TIME COMPLEXITY

    Let n  = number of documents
    Let m  = average number of unique words per document

    jaccard_similarity():
        keys_list()     -> O(m)   (scan all table slots once)
        ht2.get() loop  -> O(m)   (m lookups, each O(1) average)
        Total per pair  -> O(m)

    compute_all_similarity_scores():
        Number of pairs = n*(n-1)/2  -> O(n^2) pairs
        Each pair costs O(m)
        Total -> O(n^2 * m)

SPACE COMPLEXITY

    similarity_results list: one entry per pair -> O(n^2)
    keys1 list inside each call: O(m) (temporary, per call)

WHY JACCARD

    - Simple and well-suited for set-based text comparison
    - Works well for plagiarism detection where shared vocabulary matters
    - Pairs naturally with hash-table-based word storage
    - Easy to compute incrementally using keys_list() and get()

    Limitation:
    - Ignores word frequency (a word appearing 10 times counts the same
      as one appearing once)
    - Ignores word order (sentence structure is not captured)

    These limitations are acceptable for the scope of this project.
    A frequency-weighted or shingling approach would address them.

PROJECT ROLE

    Called from main.py after all documents have been preprocessed and
    their chaining hash tables have been built.

    Output is passed directly to merge_sort_similarity() in Sorting.py
    to produce the final ranked similarity report.


"""
