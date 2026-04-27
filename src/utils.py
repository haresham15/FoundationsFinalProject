"""
Shared Utilities
=================
Helper functions used across the tree implementations and benchmarks.
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.rbt import RedBlackTree


def generate_random_keys(n: int, seed: int = 42) -> list[int]:
    """Generate a list of n unique random integers in shuffled order."""
    rng = random.Random(seed)
    keys = list(range(1, n + 1))
    rng.shuffle(keys)
    return keys


def generate_sorted_keys(n: int) -> list[int]:
    """Generate a sorted list of integers 1..n (worst case for BST)."""
    return list(range(1, n + 1))


def generate_reverse_sorted_keys(n: int) -> list[int]:
    """Generate a reverse-sorted list of integers n..1."""
    return list(range(n, 0, -1))


def verify_rbt_height_bound(tree: RedBlackTree) -> bool:
    """
    Verify the fundamental height theorem: h <= 2 * log2(n + 1).

    This theorem ensures the Red-Black Tree remains balanced.

    Args:
        tree: A non-empty Red-Black Tree.

    Returns:
        True if the height bound is satisfied.
    """
    if tree.is_empty:
        return True
    h = tree.height()
    n = tree.size
    max_height = 2 * math.log2(n + 1)
    return h <= max_height


def tree_to_dict(tree: RedBlackTree) -> dict | None:
    """
    Convert a Red-Black Tree to a nested dictionary for serialization.

    Useful for debugging and visualization.
    """
    from src.rbt import Color

    def _node_to_dict(node):
        if node is tree.NIL:
            return None
        return {
            "key": node.key,
            "color": "RED" if node.color == Color.RED else "BLACK",
            "left": _node_to_dict(node.left),
            "right": _node_to_dict(node.right),
        }

    return _node_to_dict(tree.root)
