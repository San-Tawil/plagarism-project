# DISPLAY MODULE

def display_loading(docs):
    print("\nDOCUMENTS LOADED")

    i = 0
    while i < len(docs):
        doc_id, tokens = docs[i]
        print(doc_id, "| Word Count:", len(tokens))
        i += 1


def display_preprocessing():
    print("\nPREPROCESSING")
    print("- Converted to lowercase")
    print("- Removed punctuation")
    print("- Tokenized into words")


def display_hash_stats(doc_tables_chain, doc_tables_double):
    print("\nHASH TABLE STATS")

    i = 0
    while i < len(doc_tables_chain):
        doc_id, ht1 = doc_tables_chain[i]
        _, ht2 = doc_tables_double[i]

        print("\nDocument:", doc_id)

        print("Chaining -> Size:", ht1.size,
              "| Entries:", ht1.count,
              "| Collisions:", ht1.collisions)

        print("Double   -> Size:", ht2.size,
              "| Entries:", ht2.count,
              "| Collisions:", ht2.collisions)

        i += 1


def compare_hash_tables(doc_tables_chain, doc_tables_double):
    print("\nHASH TABLE COMPARISON")

    i = 0
    while i < len(doc_tables_chain):
        doc_id, ht1 = doc_tables_chain[i]
        _, ht2 = doc_tables_double[i]

        print("\nDocument:", doc_id)

        if ht1.collisions < ht2.collisions:
            print("Better: Chaining")
        elif ht2.collisions < ht1.collisions:
            print("Better: Double Hashing")
        else:
            print("Equal Performance")

        i += 1


def display_sorting_status(method_name, results):
    print("\nSORTING STATUS (" + method_name + ")")

    if len(results) == 0:
        print("No pairs to sort.")
        return

    is_desc_sorted = True
    i = 1
    while i < len(results):
        if results[i - 1][2] < results[i][2]:
            is_desc_sorted = False
            break
        i += 1

    if is_desc_sorted:
        print("Pairs are sorted by similarity score (descending).")
    else:
        print("Warning: pairs are not fully sorted in descending order.")

    top = results[0]
    bottom = results[len(results) - 1]
    print("Top pair:", top[0], "vs", top[1], "->", top[2])
    print("Bottom pair:", bottom[0], "vs", bottom[1], "->", bottom[2])


def display_results(results):
    print("\nSIMILARITY REPORT")

    if len(results) == 0:
        print("No results.")
        return

    print("\nRank | Document Pair        | Score   | Level")

    rank = 1
    i = 0

    while i < len(results):
        doc1, doc2, score = results[i]

        if score > 0.8:
            tag = "HIGH"
        elif score > 0.5:
            tag = "MED"
        else:
            tag = "LOW"

        score_str = str(int(score * 10000) / 10000)
        pair = doc1 + " vs " + doc2

        print(str(rank).ljust(4), "|",
              pair.ljust(20), "|",
              score_str.ljust(7), "|",
              tag)

        rank += 1
        i += 1

    print()


def display_summary(results):
    print("\nSUMMARY")

    print("Total document pairs:", len(results))

    if len(results) > 0:
        top = results[0]
        print("Most similar pair:", top[0], "and", top[1], "→", top[2])

    print()


def display_rbt_inorder(method_name, rows):
    print("\nRED-BLACK TREE INORDER (" + method_name + ")")

    if len(rows) == 0:
        print("No entries.")
        return

    print("\nRank | Document Pair        | Score   | Level")

    i = 0
    rank = 1
    while i < len(rows):
        row = rows[i]
        doc1 = str(row["doc1"])
        doc2 = str(row["doc2"])
        score = row["similarity"]

        if score > 0.8:
            tag = "HIGH"
        elif score > 0.5:
            tag = "MED"
        else:
            tag = "LOW"

        score_str = str(int(score * 10000) / 10000)
        pair = doc1 + " vs " + doc2
        print(str(rank).ljust(4), "|",
              pair.ljust(20), "|",
              score_str.ljust(7), "|",
              tag)
        rank += 1
        i += 1

    print()


def display_rbt_high_range(method_name, rows, min_val=0.8, max_val=1.0):
    print("\nRED-BLACK TREE HIGH RANGE (" + method_name + ")")
    print("Range:", min_val, "to", max_val)

    if len(rows) == 0:
        print("No HIGH-similarity pairs in range.")
        return

    print("\nRank | Document Pair        | Score   | Level")

    i = 0
    rank = 1
    while i < len(rows):
        row = rows[i]
        doc1 = str(row["doc1"])
        doc2 = str(row["doc2"])
        score = row["similarity"]

        score_str = str(int(score * 10000) / 10000)
        pair = doc1 + " vs " + doc2
        print(str(rank).ljust(4), "|",
              pair.ljust(20), "|",
              score_str.ljust(7), "|",
              "HIGH")
        rank += 1
        i += 1

    print()


"""
DISPLAY NOTES

PURPOSE:
The display module formats and presents all results clearly in the terminal,
as required by the project specification.


1. DOCUMENT LOADING DISPLAY

Shows:
    - document IDs
    - word counts

Time Complexity:
    O(n)
    n = number of documents


2. PREPROCESSING DISPLAY

Shows:
    - steps performed (lowercase, punctuation removal, tokenization)

Time Complexity:
    O(1)

Reason:
    Only prints static information


3. HASH TABLE STATS DISPLAY

Shows:
    - table size
    - number of entries
    - number of collisions
    - collision method

Time Complexity:
    O(n)
    n = number of documents

Purpose:
    Provides insight into performance of hash tables


4. HASH TABLE COMPARISON

Compares:
    - collisions in chaining vs double hashing

Time Complexity:
    O(n)

Purpose:
    Evaluates efficiency of collision handling methods


5. SIMILARITY RESULTS DISPLAY

Shows:
    - ranked document pairs
    - similarity scores
    - level tags (HIGH, MED, LOW)

Time Complexity:
    O(p)
    p = number of document pairs

Additional:
    Formatting improves readability and clarity


6. SUMMARY DISPLAY

Shows:
    - total number of pairs
    - most similar pair

Time Complexity:
    O(1)


7. DESIGN CHOICES

- Manual formatting used (no advanced libraries)
- Fixed decimal formatting for readability
- Tagging system (HIGH/MED/LOW) improves interpretation

This ensures:
    - clarity for users
    - compliance with project requirements


8. PROJECT ROLE

The display module:
    - communicates results clearly
    - helps interpret similarity scores
    - demonstrates correctness of the system

Poor display → even correct results appear confusing



"""