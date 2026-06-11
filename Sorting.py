"""
Sorting module for similarity results.

Expected tuple format:
    (doc1_id, doc2_id, score)
Sorted order:
    descending by score (highest similarity first)
"""


def _merge(left, right):
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i][2] >= right[j][2]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged


def _merge_sort(items):
    if len(items) <= 1:
        return items

    mid = len(items) // 2
    left = _merge_sort(items[:mid])
    right = _merge_sort(items[mid:])
    return _merge(left, right)


def merge_sort_similarity(results):
    """
    Sort similarity tuples in-place by score descending.

    Parameters:
        results: list of (doc1_id, doc2_id, score)
    """
    sorted_results = _merge_sort(results)
    results[:] = sorted_results