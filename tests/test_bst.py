"""
Binary Search Tree Test Suite
===============================
Correctness tests for the BST baseline implementation.
"""

import pytest
from src.bst import BinarySearchTree


@pytest.fixture
def tree():
    return BinarySearchTree()


class TestBSTBasics:
    def test_empty(self, tree):
        assert tree.is_empty
        assert tree.size == 0

    def test_insert_single(self, tree):
        tree.insert(10)
        assert tree.size == 1
        assert tree.contains(10)

    def test_insert_multiple(self, tree):
        for k in [10, 5, 15, 3, 7]:
            tree.insert(k)
        assert tree.size == 5
        assert tree.to_list() == [3, 5, 7, 10, 15]

    def test_search_hit_and_miss(self, tree):
        tree.insert(10)
        assert tree.contains(10) is True
        assert tree.contains(99) is False

    def test_delete_leaf(self, tree):
        for k in [10, 5, 15]:
            tree.insert(k)
        assert tree.delete(5)
        assert not tree.contains(5)
        assert tree.size == 2

    def test_delete_node_with_children(self, tree):
        for k in [10, 5, 15, 3, 7, 12, 20]:
            tree.insert(k)
        tree.delete(10)
        assert not tree.contains(10)
        assert tree.to_list() == [3, 5, 7, 12, 15, 20]

    def test_delete_all(self, tree):
        keys = [10, 5, 15, 3, 7]
        for k in keys:
            tree.insert(k)
        for k in keys:
            assert tree.delete(k)
        assert tree.is_empty

    def test_delete_nonexistent(self, tree):
        tree.insert(10)
        assert tree.delete(99) is False

    def test_height_sorted_input(self, tree):
        """BST degrades to O(n) height for sorted input."""
        for i in range(1, 101):
            tree.insert(i)
        # Unbalanced BST height should be ~99
        assert tree.height() == 99

    def test_minimum_maximum(self, tree):
        for k in [10, 5, 15, 3, 20]:
            tree.insert(k)
        assert tree.minimum().key == 3
        assert tree.maximum().key == 20
