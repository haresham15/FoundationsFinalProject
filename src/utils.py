
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.rbt import RedBlackTree


def generate_random_keys(n: int, seed: int = 42) -> list[int]:
    rng = random.Random(seed)
    keys = list(range(1, n + 1))
    rng.shuffle(keys)
    return keys


def generate_sorted_keys(n: int) -> list[int]:
    return list(range(1, n + 1))


def generate_reverse_sorted_keys(n: int) -> list[int]:
    return list(range(n, 0, -1))


def verify_rbt_height_bound(tree: RedBlackTree) -> bool:
    if tree.is_empty:
        return True
    h = tree.height()
    n = tree.size
    max_height = 2 * math.log2(n + 1)
    return h <= max_height

def tree_to_dict(tree: RedBlackTree) -> dict | None:
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
