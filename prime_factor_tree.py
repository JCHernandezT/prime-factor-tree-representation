import math
from itertools import combinations_with_replacement, permutations


# =====================================================================
# PRIME FACTORIZATION
# =====================================================================

def smallest_prime_factor(n):
    """Returns the smallest prime factor of abs(n)."""

    n = abs(n)

    if n <= 1:
        raise ValueError("SPF is defined here only for |n| >= 2.")

    for i in range(2, math.isqrt(n) + 1):
        if n % i == 0:
            return i

    return n


# =====================================================================
# TREE NODES
# =====================================================================

class Node:
    def evaluate(self):
        raise NotImplementedError


class RawTerm(Node):
    def __init__(self, val):
        if val == 0:
            raise ValueError("RawTerm cannot represent zero.")

        self.val = val

    def evaluate(self):
        return self.val

    def __repr__(self):
        return str(self.val)


class ScaledTerm(Node):
    def __init__(self, factor, terms):
        if factor < 2:
            raise ValueError("A ScaledTerm factor must be prime.")

        self.factor = factor
        self.terms = terms

    def evaluate(self):
        return self.factor * sum(
            term.evaluate() for term in self.terms
        )

    def __repr__(self):
        sorted_terms = sorted(self.terms, key=node_sort_key)
        inner = format_terms(sorted_terms)
        return f"{self.factor}({inner})"


# =====================================================================
# CANONICAL ORDERING AND FORMATTING
# =====================================================================

def node_sort_key(node):
    """
    Canonical ordering:
    1. RawTerm(1)
    2. RawTerm(-1)
    3. Remaining prime-associated nodes in ascending prime order.
    """

    if isinstance(node, RawTerm):

        if abs(node.val) == 1:
            return (0, 0 if node.val == 1 else 1, 0)

        return (
            1,
            abs(node.val),
            0 if node.val > 0 else 1
        )

    return (1, node.factor, 0)


def format_terms(terms):
    """Formats a list of nodes as an algebraic sum."""

    if not terms:
        return "0"

    parts = []

    for term in terms:

        expression = repr(term)

        if not parts:
            parts.append(expression)

        elif isinstance(term, RawTerm) and term.val < 0:
            parts.append(expression)

        else:
            parts.append("+" + expression)

    return "".join(parts)


def representation_string(terms):
    """Returns the canonical representation as a single expression."""

    sorted_terms = sorted(terms, key=node_sort_key)

    return format_terms(sorted_terms)


def format_single_line(terms, current_sum):
    """Formats the current sum and its representation."""

    rep = representation_string(terms)

    return f"[{current_sum}]\n{rep}"


# =====================================================================
# RECURSIVE INSERTION
# =====================================================================

def add_value(terms, v):
    """
    Adds an integer using recursive prime-factor propagation.

    Zero is ignored.
    Negative integers retain their sign through signed quotients.
    """

    # Zero does not generate a node.
    if v == 0:
        return

    # The signed units are always represented directly.
    if abs(v) == 1:
        terms.append(RawTerm(v))
        return

    # Extract the smallest prime factor from the absolute value.
    p = smallest_prime_factor(abs(v))

    # Exact division preserves the sign of v.
    q = v // p

    # Search for an existing node associated with p.
    found_container = None

    for idx, term in enumerate(terms):

        if isinstance(term, ScaledTerm) and term.factor == p:
            found_container = term
            break

        elif isinstance(term, RawTerm) and abs(term.val) == p:

            # Promote the signed prime RawTerm.
            initial_quotient = term.val // p

            new_scaled = ScaledTerm(
                p,
                [RawTerm(initial_quotient)]
            )

            terms[idx] = new_scaled
            found_container = new_scaled
            break

    if found_container is not None:

        # Recursively insert the signed quotient.
        add_value(found_container.terms, q)

    else:

        # A singleton signed prime remains a RawTerm.
        if q == 1:
            terms.append(RawTerm(p))
            return

        if q == -1:
            terms.append(RawTerm(-p))
            return

        # Otherwise, create a new ScaledTerm.
        new_scaled = ScaledTerm(p, [])

        add_value(new_scaled.terms, q)

        terms.append(new_scaled)


# =====================================================================
# REPRESENTATION GENERATION
# =====================================================================

def generate_representations(sequence_terms):
    """Generates the step-by-step representation trace."""

    terms = []
    current_sum = 0
    results = []

    for value in sequence_terms:

        current_sum += value

        add_value(terms, value)

        results.append(
            format_single_line(terms, current_sum)
        )

    return results


def build_representation(sequence_terms):
    """Builds and returns the final representation tree."""

    terms = []

    for value in sequence_terms:
        add_value(terms, value)

    return terms


def evaluate_forest(terms):
    """Evaluates a complete representation forest."""

    return sum(term.evaluate() for term in terms)


# =====================================================================
# AUTOMATED TESTS
# =====================================================================

def run_self_tests():
    """Runs correctness and permutation-invariance tests."""

    print("=== RUNNING AUTOMATED TESTS ===")

    # ---------------------------------------------------------------
    # Test 1: Basic permutation invariance
    # ---------------------------------------------------------------

    result_1 = generate_representations([2, 4])[-1]
    result_2 = generate_representations([4, 2])[-1]

    expected = "[6]\n2(1+2)"

    assert result_1 == expected, result_1
    assert result_2 == expected, result_2

    print("[PASS] Test 1: Basic permutation invariance")

    # ---------------------------------------------------------------
    # Test 2: Repeated prime insertion
    # ---------------------------------------------------------------

    result = generate_representations([2, 2])[-1]

    assert result == "[4]\n2(1+1)", result

    print("[PASS] Test 2: Repeated prime insertion")

    # ---------------------------------------------------------------
    # Test 3: Repeated composite insertion
    # ---------------------------------------------------------------

    result = generate_representations([4, 4])[-1]

    assert result == "[8]\n2(2(1+1))", result

    print("[PASS] Test 3: Repeated composite insertion")

    # ---------------------------------------------------------------
    # Test 4: Nested recursive propagation
    # ---------------------------------------------------------------

    result = generate_representations([2, 4, 8])[-1]

    assert result == "[14]\n2(1+2(1+2))", result

    print("[PASS] Test 4: Nested recursive propagation")

    # ---------------------------------------------------------------
    # Test 5: Zero handling
    # ---------------------------------------------------------------

    result = generate_representations([0, 0, 0])[-1]

    assert result == "[0]\n0", result

    result = generate_representations([1, 0, -2, 0, 3])[-1]

    assert result == "[2]\n1-2+3", result

    assert representation_string(
        build_representation([1, 0, -2, 3])
    ) == representation_string(
        build_representation([1, -2, 3])
    )

    print("[PASS] Test 5: Zero handling and no-op insertion")

    # ---------------------------------------------------------------
    # Test 6: Negative prime and composite inputs
    # ---------------------------------------------------------------

    result = generate_representations([-2])[-1]

    assert result == "[-2]\n-2", result

    result = generate_representations([-4])[-1]

    assert result == "[-4]\n2(-2)", result

    result = generate_representations([-6])[-1]

    assert result == "[-6]\n2(-3)", result

    print("[PASS] Test 6: Negative prime and composite inputs")

    # ---------------------------------------------------------------
    # Test 7: Signed prime grouping and cancellation
    # ---------------------------------------------------------------

    result = generate_representations([2, -2])[-1]

    assert result == "[0]\n2(1-1)", result

    result = generate_representations([-3, -3])[-1]

    assert result == "[-6]\n3(-1-1)", result

    print("[PASS] Test 7: Signed prime grouping and cancellation")

    # ---------------------------------------------------------------
    # Test 8: Signed recursive propagation
    # ---------------------------------------------------------------

    result = generate_representations(
        [1, -2, 3, -4]
    )[-1]

    assert result == "[-2]\n1+2(-1-2)+3", result

    result = generate_representations(
        [1, -2, 3, -4, 5, -6]
    )[-1]

    assert result == "[-3]\n1+2(-1-2-3)+3+5", result

    print("[PASS] Test 8: Signed recursive propagation")

    # ---------------------------------------------------------------
    # Test 9: Exhaustive value preservation and permutation invariance
    #
    # All multisets of up to four terms are considered.
    # Each term belongs to {-4, ..., 4}.
    # ---------------------------------------------------------------

    tested_sequences = 0

    domain = range(-4, 5)

    for length in range(1, 5):

        for multiset in combinations_with_replacement(
            domain, length
        ):

            reference_representation = None

            for sequence in set(permutations(multiset)):

                terms = []
                current_sum = 0

                for value in sequence:

                    current_sum += value

                    add_value(terms, value)

                    # Every intermediate representation must
                    # preserve the corresponding partial sum.
                    assert evaluate_forest(terms) == current_sum, (
                        f"Value mismatch: {sequence}\n"
                        f"Partial sum: {current_sum}\n"
                        f"Representation: {representation_string(terms)}"
                    )

                current_representation = representation_string(terms)

                if reference_representation is None:

                    reference_representation = current_representation

                else:

                    assert (
                        current_representation
                        == reference_representation
                    ), (
                        f"Permutation mismatch: {multiset}\n"
                        f"Expected: {reference_representation}\n"
                        f"Got: {current_representation}"
                    )

                tested_sequences += 1

    print(
        f"[PASS] Test 9: {tested_sequences} ordered sequences "
        "checked for value preservation and permutation invariance"
    )

    # ---------------------------------------------------------------
    # Test 10: Zero insertion at different positions
    # ---------------------------------------------------------------

    sequences = [
        [0, 1, -2, 3],
        [1, 0, -2, 3],
        [1, -2, 0, 3],
        [1, -2, 3, 0],
        [1, -2, 3]
    ]

    representations = [
        representation_string(build_representation(seq))
        for seq in sequences
    ]

    assert len(set(representations)) == 1, representations

    print("[PASS] Test 10: Zero-position invariance")

    print("\n=== ALL TESTS PASSED ===")


# =====================================================================
# EXECUTION BLOCK
# =====================================================================

if __name__ == "__main__":

    # Run automated correctness tests.
    run_self_tests()

    # Input sequence.
    sequence_terms = list(range(1, 36))

    print("\n=== EXACT PRIME-FACTOR TREE TRACE ===")

    results = generate_representations(sequence_terms)

    for rep in results:
        print(rep)
        print("-" * 40)