"""
Red-Black Tree Test Suite
===========================
Comprehensive unit and integration tests verifying correctness of
every RBT operation and all five Red-Black properties.
"""

import math
import random
import pytest

from src.rbt import RedBlackTree, Color, Node
from src.utils import (
    generate_random_keys,
    generate_sorted_keys,
    generate_reverse_sorted_keys,
    verify_rbt_height_bound,
)


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def tree():
    """Return a fresh, empty Red-Black Tree."""
    return RedBlackTree()


@pytest.fixture
def small_tree():
    """Return an RBT with keys [10, 20, 30, 15, 25, 5, 1]."""
    t = RedBlackTree()
    for k in [10, 20, 30, 15, 25, 5, 1]:
        t.insert(k)
    return t


# ======================================================================
# Property Validation Tests
# ======================================================================

class TestRBTProperties:
    """Test that all five RBT properties hold after various operations."""

    def test_empty_tree_is_valid(self, tree):
        assert tree.validate()

    def test_single_insert_properties(self, tree):
        tree.insert(42)
        assert tree.validate()
        assert tree.root.color == Color.BLACK  # Property 2

    def test_properties_after_sequential_inserts(self, tree):
        """Insert 1..50 in order (triggers many rotations) and validate."""
        for i in range(1, 51):
            tree.insert(i)
            assert tree.validate(), f"Properties violated after inserting {i}"

    def test_properties_after_reverse_inserts(self, tree):
        """Insert 50..1 in reverse order."""
        for i in range(50, 0, -1):
            tree.insert(i)
            assert tree.validate(), f"Properties violated after inserting {i}"

    def test_properties_after_random_inserts(self, tree):
        keys = generate_random_keys(200)
        for k in keys:
            tree.insert(k)
            assert tree.validate(), f"Properties violated after inserting {k}"

    def test_properties_after_deletions(self, tree):
        keys = generate_random_keys(100)
        for k in keys:
            tree.insert(k)

        random.seed(99)
        delete_order = keys[:]
        random.shuffle(delete_order)

        for k in delete_order:
            tree.delete(k)
            assert tree.validate(), f"Properties violated after deleting {k}"

    def test_nil_is_black(self, tree):
        assert tree.NIL.color == Color.BLACK


# ======================================================================
# Insertion Tests
# ======================================================================

class TestInsertion:
    def test_insert_single(self, tree):
        node = tree.insert(10)
        assert node.key == 10
        assert tree.root is node
        assert tree.root.color == Color.BLACK
        assert tree.size == 1

    def test_insert_multiple(self, tree):
        for k in [10, 5, 15]:
            tree.insert(k)
        assert tree.size == 3
        assert tree.to_list() == [5, 10, 15]

    def test_insert_duplicates(self, tree):
        tree.insert(10)
        tree.insert(10)
        tree.insert(10)
        assert tree.size == 3
        assert tree.validate()

    def test_insert_ascending(self, tree):
        """Sorted input — worst case for BST, RBT should stay balanced."""
        for i in range(1, 101):
            tree.insert(i)
        assert tree.validate()
        assert tree.to_list() == list(range(1, 101))
        assert tree.height() <= 2 * math.log2(101)

    def test_insert_descending(self, tree):
        for i in range(100, 0, -1):
            tree.insert(i)
        assert tree.validate()
        assert tree.to_list() == list(range(1, 101))

    def test_insert_preserves_bst_order(self, tree):
        keys = generate_random_keys(500)
        for k in keys:
            tree.insert(k)
        sorted_keys = sorted(keys)
        assert tree.to_list() == sorted_keys


# ======================================================================
# Insert Fixup Case Tests
# ======================================================================

class TestInsertFixupCases:
    """Specifically trigger each insertion fixup case."""

    def test_case_1_recoloring(self, tree):
        """
        Case I: Uncle is red → recolor.
        Insert 10, 5, 15 (root=10 black, children red).
        Insert 1 → parent(5) red, uncle(15) red → recolor.
        """
        tree.insert(10)
        tree.insert(5)
        tree.insert(15)
        tree.insert(1)
        assert tree.validate()
        # After recoloring, root stays black
        assert tree.root.color == Color.BLACK

    def test_case_2_and_3_rotations(self, tree):
        """
        Case II → Case III: Uncle is black, node is inner child.
        Insert 10, 5, then 7 (right child of 5, which is left child of 10).
        This triggers left-rotate on 5 (Case II) then right-rotate on 10 (Case III).
        """
        tree.insert(10)
        tree.insert(5)
        tree.insert(7)
        assert tree.validate()
        # After rotations, 7 should be the root
        assert tree.root.key == 7

    def test_case_3_outer_child(self, tree):
        """
        Case III directly: Uncle is black, node is outer child.
        Insert 10, 5, 1 → right-rotate on 10.
        """
        tree.insert(10)
        tree.insert(5)
        tree.insert(1)
        assert tree.validate()
        assert tree.root.key == 5

    def test_mirror_cases(self, tree):
        """Test mirror (right-side) cases."""
        tree.insert(10)
        tree.insert(20)
        tree.insert(15)  # Case II mirror → Case III mirror
        assert tree.validate()
        assert tree.root.key == 15


# ======================================================================
# Deletion Tests
# ======================================================================

class TestDeletion:
    def test_delete_from_empty(self, tree):
        assert tree.delete(10) is False

    def test_delete_nonexistent(self, small_tree):
        assert small_tree.delete(999) is False
        assert small_tree.size == 7

    def test_delete_leaf(self, tree):
        tree.insert(10)
        tree.insert(5)
        tree.insert(15)
        assert tree.delete(5) is True
        assert tree.size == 2
        assert tree.validate()
        assert not tree.contains(5)

    def test_delete_node_with_one_child(self, tree):
        for k in [10, 5, 15, 3]:
            tree.insert(k)
        tree.delete(5)
        assert tree.validate()
        assert tree.contains(3)
        assert not tree.contains(5)

    def test_delete_node_with_two_children(self, tree):
        for k in [10, 5, 15, 3, 7, 12, 20]:
            tree.insert(k)
        tree.delete(10)
        assert tree.validate()
        assert not tree.contains(10)
        remaining = [3, 5, 7, 12, 15, 20]
        assert tree.to_list() == remaining

    def test_delete_root(self, tree):
        tree.insert(10)
        assert tree.delete(10) is True
        assert tree.is_empty
        assert tree.size == 0

    def test_delete_all_nodes(self, tree):
        keys = list(range(1, 21))
        for k in keys:
            tree.insert(k)
        for k in keys:
            assert tree.delete(k) is True
            assert tree.validate()
        assert tree.is_empty
        assert tree.size == 0

    def test_delete_random_order(self, tree):
        """Insert 1..100, delete in random order, validate after each."""
        keys = list(range(1, 101))
        for k in keys:
            tree.insert(k)

        rng = random.Random(77)
        rng.shuffle(keys)
        for k in keys:
            tree.delete(k)
            assert tree.validate()


# ======================================================================
# Search Tests
# ======================================================================

class TestSearch:
    def test_search_empty_tree(self, tree):
        result = tree.search(10)
        assert result is tree.NIL

    def test_search_hit(self, small_tree):
        node = small_tree.search(15)
        assert node is not small_tree.NIL
        assert node.key == 15

    def test_search_miss(self, small_tree):
        assert small_tree.search(99) is small_tree.NIL

    def test_contains(self, small_tree):
        assert small_tree.contains(10) is True
        assert small_tree.contains(99) is False

    def test_minimum(self, small_tree):
        assert small_tree.minimum().key == 1

    def test_maximum(self, small_tree):
        assert small_tree.maximum().key == 30


# ======================================================================
# Rotation Tests
# ======================================================================

class TestRotations:
    def test_left_rotate_preserves_order(self, tree):
        """After left rotation, in-order traversal should still be sorted."""
        for k in [10, 5, 15, 12, 20]:
            tree.insert(k)
        original_order = tree.to_list()
        # Manually trigger a left rotation on a node
        node = tree.search(10)
        if node.right is not tree.NIL:
            tree._left_rotate(node)
        # BST order must still hold
        # (Note: RBT properties may be violated — this tests BST ordering only)
        assert tree.to_list() == original_order

    def test_right_rotate_preserves_order(self, tree):
        for k in [10, 5, 15, 3, 7]:
            tree.insert(k)
        original_order = tree.to_list()
        node = tree.search(10)
        if node.left is not tree.NIL:
            tree._right_rotate(node)
        assert tree.to_list() == original_order


# ======================================================================
# Traversal Tests
# ======================================================================

class TestTraversals:
    def test_inorder_sorted(self, small_tree):
        keys = [n.key for n in small_tree.inorder()]
        assert keys == sorted(keys)

    def test_preorder(self, small_tree):
        keys = [n.key for n in small_tree.preorder()]
        assert len(keys) == 7

    def test_postorder(self, small_tree):
        keys = [n.key for n in small_tree.postorder()]
        assert len(keys) == 7

    def test_level_order(self, small_tree):
        levels = list(small_tree.level_order())
        assert len(levels) > 0
        # First level is just the root
        assert len(levels[0]) == 1
        # Total nodes across all levels equals tree size
        total = sum(len(lvl) for lvl in levels)
        assert total == small_tree.size

    def test_to_list(self, small_tree):
        assert small_tree.to_list() == [1, 5, 10, 15, 20, 25, 30]


# ======================================================================
# Metrics Tests
# ======================================================================

class TestMetrics:
    def test_height_empty(self, tree):
        assert tree.height() == -1

    def test_height_single(self, tree):
        tree.insert(10)
        assert tree.height() == 0

    def test_height_bound(self, tree):
        """Verify h <= 2 * log2(n+1) for n=1000."""
        for k in generate_random_keys(1000):
            tree.insert(k)
        assert verify_rbt_height_bound(tree)

    def test_height_bound_sorted_input(self, tree):
        """Sorted input — the pathological case for BSTs."""
        for k in generate_sorted_keys(1000):
            tree.insert(k)
        assert verify_rbt_height_bound(tree)

    def test_black_height(self, small_tree):
        bh = small_tree.black_height()
        assert bh >= 1

    def test_size_tracking(self, tree):
        assert tree.size == 0
        tree.insert(10)
        assert tree.size == 1
        tree.insert(20)
        assert tree.size == 2
        tree.delete(10)
        assert tree.size == 1


# ======================================================================
# Integration Tests
# ======================================================================

class TestIntegration:
    def test_insert_then_search_all(self, tree):
        """Insert N keys, verify every key is searchable."""
        keys = generate_random_keys(500)
        for k in keys:
            tree.insert(k)
        for k in keys:
            assert tree.contains(k), f"Key {k} not found after insertion"

    def test_insert_then_delete_all(self, tree):
        """Insert N keys, delete all in different order, verify empty."""
        keys = generate_random_keys(500)
        for k in keys:
            tree.insert(k)

        rng = random.Random(12345)
        delete_order = keys[:]
        rng.shuffle(delete_order)

        for k in delete_order:
            assert tree.delete(k) is True
        assert tree.is_empty
        assert tree.size == 0

    def test_interleaved_operations(self, tree):
        """Mix insert, delete, and search operations randomly."""
        rng = random.Random(54321)
        inserted = set()

        for _ in range(2000):
            op = rng.choice(["insert", "insert", "insert", "delete", "search"])
            key = rng.randint(1, 500)

            if op == "insert":
                if key not in inserted:
                    tree.insert(key)
                    inserted.add(key)
            elif op == "delete" and key in inserted:
                assert tree.delete(key) is True
                inserted.discard(key)
            elif op == "search":
                result = tree.contains(key)
                assert result == (key in inserted), \
                    f"Search({key}) returned {result}, expected {key in inserted}"

            assert tree.validate()

    def test_stress_10000_operations(self, tree):
        """Stress test: 10,000 random ops with validation."""
        rng = random.Random(99999)
        present = set()

        for _ in range(10_000):
            key = rng.randint(1, 2000)
            if rng.random() < 0.6:
                if key not in present:
                    tree.insert(key)
                    present.add(key)
            else:
                if key in present:
                    assert tree.delete(key) is True
                    present.discard(key)

        # Final validation
        assert tree.validate()
        assert tree.size == len(present)

        # All remaining keys are findable
        for k in present:
            assert tree.contains(k)

    def test_sorted_input_height_guarantee(self, tree):
        """Insert 1..N sorted, verify height stays O(log n)."""
        n = 5000
        for i in range(1, n + 1):
            tree.insert(i)
        h = tree.height()
        max_h = 2 * math.log2(n + 1)
        assert h <= max_h, f"Height {h} exceeds bound {max_h:.1f} for n={n}"

    def test_string_representation(self, tree):
        """Ensure __str__ works on empty and non-empty trees."""
        assert str(tree) == "(empty tree)"
        tree.insert(10)
        tree.insert(5)
        tree.insert(15)
        s = str(tree)
        assert "10" in s
        assert "5" in s
        assert "15" in s
