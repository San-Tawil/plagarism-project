"""
IMPROVED DIVIDE-AND-CONQUER POSITIONAL SIMILARITY MODULE

Enhancements:
- Window-based positional tolerance
- N-gram matching (phrase-level comparison)
- Robust normalization
- Preserves recursion + divide-and-conquer design
"""


def get_ngram(tokens, index, n):
    """Return n-gram tuple starting at index, or None if out of bounds."""
    if index + n > len(tokens):
        return None
    return tuple(tokens[index:index + n])


def match_in_window(tokens1, tokens2, index, window, n):
    """
    Check if n-gram at tokens1[index] exists within a window in tokens2.
    """
    ngram1 = get_ngram(tokens1, index, n)
    if ngram1 is None:
        return 0

    left = max(0, index - window)
    right = min(len(tokens2) - 1, index + window)

    k = left
    while k <= right:
        ngram2 = get_ngram(tokens2, k, n)
        if ngram1 == ngram2:
            return 1
        k += 1

    return 0


def recursive_similarity(tokens1, tokens2, start, end, window=2, n=2):
    """
    Recursively compute tolerant positional similarity using divide-and-conquer.
    """
    if start > end:
        return 0

    if start == end:
        return match_in_window(tokens1, tokens2, start, window, n)

    mid = (start + end) // 2

    left_score = recursive_similarity(tokens1, tokens2, start, mid, window, n)
    right_score = recursive_similarity(tokens1, tokens2, mid + 1, end, window, n)

    return left_score + right_score


def positional_similarity_score(tokens1, tokens2, window=2, n=2):
    """
    Compute normalized positional similarity score.

    Uses max length for normalization to avoid inflated similarity.
    """
    if not tokens1 or not tokens2:
        return 0.0

    length = max(len(tokens1), len(tokens2))

    matches = recursive_similarity(
        tokens1,
        tokens2,
        0,
        min(len(tokens1), len(tokens2)) - 1,
        window,
        n
    )

    return matches / length


def compute_all_divide_conquer_scores(doc_tokens, window=2, n=2):
    """
    Compute pairwise improved positional similarity scores.

    Parameters:
        doc_tokens: list of (doc_id, token_list)
        window: positional tolerance
        n: n-gram size

    Returns:
        list of (doc_id_1, doc_id_2, score)
    """
    results = []
    total = len(doc_tokens)

    for i in range(total):
        for j in range(i + 1, total):
            doc1_id, tokens1 = doc_tokens[i]
            doc2_id, tokens2 = doc_tokens[j]

            score = positional_similarity_score(tokens1, tokens2, window, n)
            results.append((doc1_id, doc2_id, score))

    return results

