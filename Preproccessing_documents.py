# PREPROCESSING MODULE

import string


def preprocess_document_text(raw_text):
    # Step 1: convert text to lowercase
    lowercase_text = raw_text.lower()

    # Step 2: replace punctuation with spaces so words don't merge
    cleaned_characters = []

    i = 0
    while i < len(lowercase_text):
        character = lowercase_text[i]
        if character not in string.punctuation:
            cleaned_characters.append(character)
        else:
            cleaned_characters.append(" ")
        i += 1

    cleaned_text = "".join(cleaned_characters)

    # Step 3: split on whitespace to produce a list of word tokens
    word_tokens = cleaned_text.split()

    return word_tokens


"""
PREPROCESSING NOTES

PURPOSE:
    Normalizes raw document text before it is stored in the hash table
    or used for similarity computation.
    Removes surface-level differences (casing, punctuation) so the
    similarity algorithm compares actual content, not formatting.

FUNCTION: preprocess_document_text(raw_text)

Parameters:
    raw_text (str) : raw string content of a document

Returns:
    list of str : cleaned, lowercase word tokens

Steps:
    1. Lowercase  -> eliminates case differences ("The" == "the")
    2. Punctuation removal -> punctuation is replaced with a space,
       not deleted outright, so "end.Start" becomes "end Start"
       rather than "endStart" (two separate tokens, not one merged token)
    3. Tokenize -> str.split() splits on any whitespace and ignores
       consecutive spaces produced by step 2

TIME COMPLEXITY:

    Let n = number of characters in the document

    Step 1 (lowercase):          O(n)  - one pass over all characters
    Step 2 (punctuation removal): O(n)  - one pass, O(1) set lookup per char
    Step 3 (split/tokenize):     O(n)  - one pass over cleaned string

    Total: O(n)

    Each step is linear. They do not nest, so complexity does not multiply.

SPACE COMPLEXITY:

    O(n)

    - lowercase_text  : copy of input            -> O(n)
    - cleaned_characters list                    -> O(n)
    - cleaned_text string                        -> O(n)
    - word_tokens list                           -> O(n)

    All intermediate structures are proportional to input size.
    No additional data structures are created.

DESIGN CHOICES:

    - Punctuation is replaced with a space (not deleted) to prevent
      accidental word merging at sentence boundaries.
    - str.split() (no argument) handles multiple consecutive spaces
      cleanly, which arise after punctuation replacement.
    - Stopword removal and stemming are not applied in this version.
      They could improve similarity quality but add complexity. The
      current implementation satisfies the minimum project requirements.
    - The function returns a plain list of tokens (not a set) so that
      word frequency information is preserved for the hash table step.

PROJECT ROLE:

    Called on every document after loading.
    Output (token list) is passed to build_table_chaining() and
    build_table_double() in hashing.py to construct word-frequency
    hash tables for each document.


"""
