# HASH TABLES MODULE


# SEPARATE CHAINING

class Node:
    def __init__(self, key, value):
        self.key   = key
        self.value = value
        self.next  = None


class HashTableChaining:
    def __init__(self, size):
        self.size       = size
        self.table      = [None] * size
        self.count      = 0
        self.collisions = 0

    def _hash(self, key):
        BASE = 31
        h    = 0
        i    = 0

        while i < len(key):
            h = (h * BASE + ord(key[i])) % self.size
            i += 1

        return h

    def insert(self, key):
        index   = self._hash(key)
        current = self.table[index]

        # if key already exists, increment its frequency count
        while current is not None:
            if current.key == key:
                current.value += 1
                return
            current = current.next

        # bucket was occupied -> collision
        if self.table[index] is not None:
            self.collisions += 1

        # insert new node at head of chain
        new_node       = Node(key, 1)
        new_node.next  = self.table[index]
        self.table[index] = new_node
        self.count    += 1

    def get(self, key):
        index   = self._hash(key)
        current = self.table[index]

        while current is not None:
            if current.key == key:
                return current.value
            current = current.next

        return 0   # key not found

    def keys_list(self):
        result = []
        i      = 0

        while i < self.size:
            current = self.table[i]
            while current is not None:
                result.append(current.key)
                current = current.next
            i += 1

        return result


# DOUBLE HASHING

class HashTableDouble:
    def __init__(self, size):
        self.size       = size
        self.keys       = [None] * size
        self.values     = [0]    * size
        self.count      = 0
        self.collisions = 0

    def _hash1(self, key):
        BASE = 31
        h    = 0
        i    = 0

        while i < len(key):
            h = (h * BASE + ord(key[i])) % self.size
            i += 1

        return h

    def _hash2(self, key):
        # step size is always >= 1 and < size so probing covers all slots
        BASE = 17
        h    = 0
        i    = 0

        while i < len(key):
            h = (h * BASE + ord(key[i])) % self.size
            i += 1

        return (h % (self.size - 1)) + 1

    def insert(self, key):
        index1 = self._hash1(key)
        index2 = self._hash2(key)

        i = 0
        while i < self.size:
            index = (index1 + i * index2) % self.size

            if self.keys[index] is None:
                # empty slot -> insert new entry
                self.keys[index]   = key
                self.values[index] = 1
                self.count        += 1
                return

            if self.keys[index] == key:
                # key exists -> increment frequency
                self.values[index] += 1
                return

            # slot occupied by a different key -> collision
            self.collisions += 1
            i += 1

    def get(self, key):
        index1 = self._hash1(key)
        index2 = self._hash2(key)

        i = 0
        while i < self.size:
            index = (index1 + i * index2) % self.size

            if self.keys[index] is None:
                return 0   # empty slot means key was never inserted

            if self.keys[index] == key:
                return self.values[index]

            i += 1

        return 0

    def keys_list(self):
        result = []
        i      = 0

        while i < self.size:
            if self.keys[i] is not None:
                result.append(self.keys[i])
            i += 1

        return result


# HELPERS

def _next_prime(n):
    """Return the smallest prime >= n. Used to pick a good table size."""
    def is_prime(x):
        if x < 2:
            return False
        d = 2
        while d * d <= x:
            if x % d == 0:
                return False
            d += 1
        return True

    candidate = n
    while not is_prime(candidate):
        candidate += 1
    return candidate


# BUILDERS

def build_table_chaining(tokens):
    # size = next prime >= 2 * unique estimated tokens for load factor ~0.5
    size = _next_prime(max(101, len(tokens) * 2))
    ht   = HashTableChaining(size)

    i = 0
    while i < len(tokens):
        ht.insert(tokens[i])
        i += 1

    return ht


def build_table_double(tokens):
    # open addressing needs low load factor; size >= 2x token count
    size = _next_prime(max(101, len(tokens) * 2))
    ht   = HashTableDouble(size)

    i = 0
    while i < len(tokens):
        ht.insert(tokens[i])
        i += 1

    return ht


"""
HASH TABLE NOTES

PURPOSE:
    Stores word frequencies for each document using two different
    collision-handling strategies so they can be compared.
    Used by the Jaccard similarity module for set intersection/union
    computation without relying on Python's built-in dict or set.

1. HASH FUNCTION

    Formula: h = (h * BASE + ord(char)) % size

    - Polynomial rolling hash; each character contributes to the hash value.
    - BASE = 31 (standard for lowercase ASCII strings).
    - Modulo table size at each step prevents integer overflow.

    Time Complexity: O(k)  where k = number of characters in the key.

2. TABLE SIZE SELECTION

    Table size is computed at build time as the next prime >= 2 * len(tokens).
    This targets a load factor of ~0.5, which:
        - minimises collisions for open addressing
        - keeps chaining chains short
    A prime size reduces clustering because fewer keys share common factors
    with the modulus.

    Minimum size is capped at 101 so small documents still use a reasonable table.

3. SEPARATE CHAINING

    Structure:  array of linked lists (Node objects)

    Collision handling:
        Multiple keys that hash to the same index are stored in a
        singly-linked list at that bucket. Traversal finds or inserts the key.

    insert():
        - Walk the chain at index; if key found, increment value.
        - If slot was non-empty before insertion, record a collision.
        Average O(1) | Worst O(n) (all keys in one bucket)

    get():
        - Walk the chain at index; return value if key found, else 0.
        Average O(1) | Worst O(n)

    Space: O(n + m)   n = unique keys, m = table size

    Strengths:  handles high load gracefully; simple to implement.
    Weaknesses: pointer chasing is cache-unfriendly; extra node memory.

4. DOUBLE HASHING (open addressing)

    Structure:  two parallel arrays: keys[] and values[]

    Collision handling:
        probe sequence: index = (h1(key) + i * h2(key)) % size
        h2 is always >= 1, so the probe visits every slot before repeating.

    insert():
        - Probe until an empty slot or matching key is found.
        - Each probe past an occupied slot counts as a collision.
        Average O(1) | Worst O(n)

    get():
        - Probe same sequence; stop at empty slot (key absent) or match.
        Average O(1) | Worst O(n)

    Space: O(m)   m = table size (no extra node objects)

    Strengths:  cache-friendly; less memory than chaining.
    Weaknesses: performance degrades near full capacity; cannot exceed size.

5. COLLISION COUNTING

    Chaining:  a collision is recorded when a new key is inserted into
               a bucket that already contains at least one node.

    Double hashing: a collision is recorded for each probe step that
                    encounters an occupied slot before finding the target.

    These counts are displayed by the display module for comparison.

6. PROJECT ROLE

    build_table_chaining() and build_table_double() are called once per
    document in main.py after preprocessing.

    The resulting hash table objects are:
        - passed to display_hash_stats() for statistics reporting
        - passed to compute_all_similarity_scores() in Jaccard.py
          where keys_list() and get() are used to compute intersection
          and union without any Python set or dict.


"""
