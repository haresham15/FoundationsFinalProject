"""
AVL Tree Test Suite
=====================
Correctness tests for the AVL Tree comparison implementation.
"""

import pytest
from src.avl import AVLTree


@pytest.fixture
def tree():
    return AVLTree()


class TestAVLBasics:
    def test_empty(self, tree):
        assert tree.is_empty
        assert tree.size == 0

    def test_insert_single(self, tree):
        tree.insert(10)
        assert tree.size == 1
        assert tree.contains(10)

    def test_insert_sorted(self, tree):
        """AVL should stay balanced even with sorted input."""
        for i in range(1, 101):
            tree.insert(i)
        assert tree.size == 100
        assert tree.to_list() == list(range(1, 101))
        # AVL height should be O(log n)
        h = tree.height()
        assert h <= 10  # log2(100) ≈ 6.6, AVL bound is ~1.44*log2(n)

    def test_insert_reverse_sorted(self, tree):
        for i in range(100, 0, -1):
            tree.insert(i)
        assert tree.to_list() == list(range(1, 101))
        assert tree.height() <= 10

    def test_search_hit_and_miss(self, tree):
        for k in [10, 5, 15]:
            tree.insert(k)
        assert tree.contains(10) is True
        assert tree.contains(99) is False

    def test_delete_leaf(self, tree):
        for k in [10, 5, 15]:
            tree.insert(k)
        assert tree.delete(5)
        assert not tree.contains(5)

    def test_delete_node_with_children(self, tree):
        for k in [10, 5, 15, 3, 7, 12, 20]:
            tree.insert(k)
        assert tree.delete(10)
        assert not tree.contains(10)
        remaining = [3, 5, 7, 12, 15, 20]
        assert tree.to_list() == remaining

    def test_delete_all(self, tree):
        keys = list(range(1, 51))
        for k in keys:
            tree.insert(k)
        for k in keys:
            assert tree.delete(k)
        assert tree.is_empty

    def test_delete_nonexistent(self, tree):
        tree.insert(10)
        assert tree.delete(99) is False

    def test_balance_maintained(self, tree):
        """Insert many items and verify height stays logarithmic."""
        import random
        rng = random.Random(42)
        keys = list(range(1, 1001))
        rng.shuffle(keys)
        for k in keys:
            tree.insert(k)
        # AVL height for n=1000 should be ≤ ~15
        assert tree.height() <= 15

    def test_minimum(self, tree):
        for k in [10, 5, 15, 3, 20]:
            tree.insert(k)
        assert tree.minimum().key == 3
