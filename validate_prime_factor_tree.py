
import math
import random
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


def is_prime(n):
    """Checks whether a positive integer is prime."""

    if n < 2:
        return False

    for i in range(2, math.isqrt(n) + 1):
        if n % i == 0:
            return False

    return True


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
        if not is_prime(factor):
            raise ValueError("ScaledTerm factor must be prime.")

        self.factor = factor
        self.terms = terms

    def evaluate(self):
        return self.factor * sum(
            term.evaluate() for term in self.terms
        )

    def __repr__(self):
        sorted_terms = sorted(
            self.terms,
            key=node_sort_key
        )

        inner = format_terms(sorted_terms)

        return f"{self.factor}({inner})"


# =====================================================================
# CANONICAL ORDERING AND FORMATTING
# =====================================================================

def node_sort_key(node):
    """Returns the canonical sorting key for a node."""

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
    """Formats nodes as an algebraic sum."""

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
    """Returns the canonical representation."""

    sorted_terms = sorted(terms, key=node_sort_key)

    return format_terms(sorted_terms)


# =====================================================================
# RECURSIVE INSERTION
# =====================================================================

def add_value(terms, v):
    """Adds an integer using recursive prime-factor propagation."""

    # Zero does not generate a node.
    if v == 0:
        return

    # Signed units are represented directly.
    if abs(v) == 1:
        terms.append(RawTerm(v))
        return

    # Extract the smallest prime factor from abs(v).
    p = smallest_prime_factor(abs(v))

    # The quotient retains the original sign.
    q = v // p

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

        add_value(found_container.terms, q)

    else:

        # A singleton signed prime remains a RawTerm.
        if q == 1:
            terms.append(RawTerm(p))
            return

        if q == -1:
            terms.append(RawTerm(-p))
            return

        new_scaled = ScaledTerm(p, [])

        add_value(new_scaled.terms, q)

        terms.append(new_scaled)


# =====================================================================
# REPRESENTATION GENERATION
# =====================================================================

def representation_string_from_sequence(sequence):
    """Builds and formats a representation from a sequence."""

    terms = []

    for value in sequence:
        add_value(terms, value)

    return representation_string(terms)


def generate_representations(sequence_terms):
    """Generates the step-by-step representation trace."""

    terms = []
    current_sum = 0
    results = []

    for value in sequence_terms:

        current_sum += value

        add_value(terms, value)

        results.append(
            f"[{current_sum}]\n{representation_string(terms)}"
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
# STRUCTURAL VALIDATION
# =====================================================================

def validate_tree(terms, parent_factor=None):
    """
    Checks structural invariants of the representation tree.

    - RawTerm may represent 1, -1, p or -p.
    - ScaledTerm factors must be positive primes.
    - Zero cannot occur as a node.
    - Each prime factor appears at most once at each level.
    - Prime factors are nondecreasing along each path.
    - ScaledTerm nodes must contain at least one child.
    """

    seen_factors = set()

    for term in terms:

        if isinstance(term, RawTerm):

            if not isinstance(term.val, int):
                return False

            if term.val == 0:
                return False

            # Signed units are allowed at every level.
            if abs(term.val) == 1:
                continue

            # Signed prime RawTerms are checked by absolute value.
            factor = abs(term.val)

            if not is_prime(factor):
                return False

        elif isinstance(term, ScaledTerm):

            # ScaledTerm factors must be positive primes.
            if not isinstance(term.factor, int):
                return False

            if not is_prime(term.factor):
                return False

            if not term.terms:
                return False

            factor = term.factor

            # Validate the internal representation recursively.
            if not validate_tree(term.terms, factor):
                return False

        else:
            return False

        # No repeated prime-associated nodes at the same level.
        if factor in seen_factors:
            return False

        seen_factors.add(factor)

        # Prime factors cannot decrease along a path.
        if parent_factor is not None and factor < parent_factor:
            return False

    return True


# =====================================================================
# AUTOMATED TESTS
# =====================================================================

def run_self_tests():
    """Runs correctness, structural and permutation tests."""

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
    # Test 5: Exhaustive positive-input validation
    #
    # All multisets of up to five terms are tested.
    # Each term ranges from 1 to 12.
    # ---------------------------------------------------------------

    tested_sequences = 0

    for length in range(1, 6):

        for multiset in combinations_with_replacement(
            range(1, 13), length
        ):

            reference_representation = None

            for sequence in set(permutations(multiset)):

                terms = []
                current_sum = 0

                for value in sequence:

                    current_sum += value

                    add_value(terms, value)

                    evaluated_sum = evaluate_forest(terms)

                    assert evaluated_sum == current_sum, (
                        f"Value preservation failed:\n"
                        f"Sequence: {sequence}\n"
                        f"Partial sum: {current_sum}\n"
                        f"Evaluated: {evaluated_sum}"
                    )

                current_representation = representation_string(terms)

                if reference_representation is None:

                    reference_representation = current_representation

                else:

                    assert (
                        current_representation
                        == reference_representation
                    ), (
                        f"Permutation mismatch:\n"
                        f"Multiset: {multiset}\n"
                        f"Expected: {reference_representation}\n"
                        f"Got: {current_representation}"
                    )

                tested_sequences += 1

    print(
        f"[PASS] Test 5: {tested_sequences} positive ordered sequences "
        "checked for value preservation and permutation invariance"
    )

    # ---------------------------------------------------------------
    # Test 6: Exhaustive signed-input validation
    #
    # All multisets of up to four terms are tested.
    # Each term ranges from -4 to 4, including zero.
    # ---------------------------------------------------------------

    signed_sequences = 0

    for length in range(1, 5):

        for multiset in combinations_with_replacement(
            range(-4, 5), length
        ):

            reference_representation = None

            for sequence in set(permutations(multiset)):

                terms = []
                current_sum = 0

                for value in sequence:

                    current_sum += value

                    add_value(terms, value)

                    assert evaluate_forest(terms) == current_sum, (
                        f"Signed value-preservation failure:\n"
                        f"Sequence: {sequence}\n"
                        f"Partial sum: {current_sum}\n"
                        f"Representation: {representation_string(terms)}"
                    )

                    assert validate_tree(terms), (
                        f"Structural failure:\n"
                        f"Sequence: {sequence}\n"
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
                        f"Signed permutation mismatch:\n"
                        f"Multiset: {multiset}\n"
                        f"Expected: {reference_representation}\n"
                        f"Got: {current_representation}"
                    )

                signed_sequences += 1

    print(
        f"[PASS] Test 6: {signed_sequences} signed ordered sequences "
        "checked for value preservation, permutation invariance "
        "and structural validity"
    )

    # ---------------------------------------------------------------
    # Test 7: Randomized signed large-integer validation
    #
    # 2,000 deterministic random sequences.
    # Lengths range from 1 to 30.
    # Values range from -10,000 to 10,000.
    # ---------------------------------------------------------------

    rng = random.Random(20261030)

    random_sequences = 2000
    random_insertions = 0

    for _ in range(random_sequences):

        length = rng.randint(1, 30)

        sequence = [
            rng.randint(-10000, 10000)
            for _ in range(length)
        ]

        terms = []
        current_sum = 0

        for value in sequence:

            current_sum += value

            add_value(terms, value)

            evaluated_sum = evaluate_forest(terms)

            assert evaluated_sum == current_sum, (
                f"Random value-preservation failure:\n"
                f"Sequence: {sequence}\n"
                f"Partial sum: {current_sum}\n"
                f"Evaluated: {evaluated_sum}"
            )

            assert validate_tree(terms), (
                f"Random structural validation failure:\n"
                f"Sequence: {sequence}\n"
                f"Representation: {representation_string(terms)}"
            )

            random_insertions += 1

    print(
        f"[PASS] Test 7: {random_sequences} signed random sequences "
        f"and {random_insertions} insertions checked"
    )

    # ---------------------------------------------------------------
    # Test 8: Targeted structural validation
    # ---------------------------------------------------------------

    structural_cases = [
        [1],
        [-1],
        [0, 0, 0],
        [2, 4],
        [-2, -4],
        [4, 4],
        [-4, -4],
        [2, 4, 8],
        [1, -2, 3, -4],
        [1, -2, 3, -4, 5, -6],
        [2, -2],
        [3, -3],
        [2, 3, 5, 7, 11, 13],
        [8, 16, 32, 64, 128],
        [-8, -16, -32, -64, -128],
        [9, 27, 81, 243],
        [-9, -27, -81, -243],
        [30, 42, 70, 105, 210],
        [-30, 42, -70, 105, -210],
        [2310, 4620, 6930, 11550],
        [-2310, 4620, -6930, 11550],
        [9991, 9999, 10000, -9973]
    ]

    for sequence in structural_cases:

        terms = build_representation(sequence)

        assert evaluate_forest(terms) == sum(sequence), (
            f"Targeted value-preservation failure:\n"
            f"Sequence: {sequence}"
        )

        assert validate_tree(terms), (
            f"Targeted structural validation failed:\n"
            f"Sequence: {sequence}\n"
            f"Representation: {representation_string(terms)}"
        )

    print(
        "[PASS] Test 8: Structural invariants "
        "checked on targeted signed and positive trees"
    )

    # ---------------------------------------------------------------
    # Test 9: Randomized structural validation
    # ---------------------------------------------------------------

    rng = random.Random(20261030)

    for _ in range(500):

        sequence = [
            rng.randint(-10000, 10000)
            for _ in range(rng.randint(1, 30))
        ]

        terms = build_representation(sequence)

        assert validate_tree(terms), (
            f"Random structural validation failed:\n"
            f"Sequence: {sequence}\n"
            f"Representation: {representation_string(terms)}"
        )

        assert evaluate_forest(terms) == sum(sequence)

    print(
        "[PASS] Test 9: Structural invariants "
        "checked on 500 additional random signed trees"
    )

    # ---------------------------------------------------------------
    # Test 10: Prime powers and composite edge cases
    # ---------------------------------------------------------------

    edge_cases = [
        [2 ** i for i in range(1, 16)],
        [-(2 ** i) for i in range(1, 16)],
        [3 ** i for i in range(1, 10)],
        [-(3 ** i) for i in range(1, 10)],
        [5 ** i for i in range(1, 8)],
        [-(5 ** i) for i in range(1, 8)],
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
        [-2, -3, -5, -7, -11, -13, -17, -19, -23, -29],
        [4, 9, 25, 49, 121, 169, 289],
        [-4, -9, -25, -49, -121, -169, -289],
        [12, 18, 20, 28, 44, 52, 68, 76],
        [-12, 18, -20, 28, -44, 52, -68, 76],
        [30, 60, 90, 120, 150, 210, 330],
        [-30, 60, -90, 120, -150, 210, -330],
        [2310, 30030, 510510],
        [-2310, -30030, -510510],
        [9991, 9999, 10000, 9973, 9967],
        [-9991, -9999, -10000, -9973, -9967],
        [0, 0, 1, -1, 2, -2, 4, -4]
    ]

    for sequence in edge_cases:

        terms = build_representation(sequence)

        assert evaluate_forest(terms) == sum(sequence), (
            f"Edge-case value preservation failed:\n"
            f"Sequence: {sequence}"
        )

        assert validate_tree(terms), (
            f"Edge-case structural validation failed:\n"
            f"Sequence: {sequence}\n"
            f"Representation: {representation_string(terms)}"
        )

    print(
        "[PASS] Test 10: Prime powers, signed composites "
        "and zero edge cases"
    )

    print("\n=== ALL TESTS PASSED ===")


# =====================================================================
# EXECUTION BLOCK
# =====================================================================

if __name__ == "__main__":

    # Run automated correctness tests.
    run_self_tests()

    # Positive triangular-number example.
    sequence_terms = list(range(1, 36))

    print("\n=== EXACT PRIME-FACTOR TREE TRACE ===")

    results = generate_representations(sequence_terms)

    for rep in results:
        print(rep)
        print("-" * 40)
