# Recursive Prime-Factor Tree Representation

This repository contains the Python implementation and computational validation of the recursive prime-factor tree representation introduced in the research note "*On a Recursive Prime-Factor Tree Representation for Partial Sums of Integer Sequences*"[doi:10.5281/zenodo.23831576](https://doi.org/10.5281/zenodo.23831576).

The implementation supports finite sequences of integers, including positive integers, negative integers, and zero.

## Requirements

- Python 3
- No third-party dependencies required (Python standard library only).

## Scripts

### `prime_factor_tree.py`

Implements the recursive prime-factor tree representation.

**Key features:**
- Recursive construction based on the smallest prime factor (SPF).
- Representation using `RawTerm` and `ScaledTerm` nodes.
- Support for positive and negative integers.
- Handling of zero as a neutral input.
- Evaluation of the resulting representation.

### `validate_prime_factor_tree.py`

Performs computational tests to validate the implementation and its structural properties.

**Validation includes:**
- Preservation of the original sum.
- Invariance under permutations of the input sequence.
- Structural consistency of the prime-factor tree.
- Exhaustive and randomized tests.
- Special cases involving negative integers, zero, prime powers, and repeated factors.

## Usage

Run either script directly from the repository directory:

```bash
python prime_factor_tree.py
```

To run the computational validation:

```bash
python validate_prime_factor_tree.py
```

## Citation

If you use this implementation in your research, please cite the associated research note:

Juan Camilo Hernández-Torres (2026). *Recursive Prime-Factor Tree Representation: Python Implementation
and Computational Tests* [doi:10.5281/zenodo.23831528](https://doi.org/10.5281/zenodo.23831528).

