"""
Binary Search Tree Implementation
===================================
A standard (unbalanced) binary search tree used as a baseline for
performance comparison against the Red-Black Tree and AVL Tree.

All operations are O(h) where h is the tree height, which can degrade
to O(n) for sorted input.
"""

from __future__ import annotations
from typing import Generator, Optional


class BSTNode:
    """A node in a Binary Search Tree."""

    __slots__ = ("key", "left", "right", "parent")

    def __init__(
        self,
        key: int,
        left: Optional[BSTNode] = None,
        right: Optional[BSTNode] = None,
        parent: Optional[BSTNode] = None,
    ) -> None:
        self.key = key
        self.left = left
        self.right = right
        self.parent = parent

    def __repr__(self) -> str:
        return f"BSTNode({self.key})"


class BinarySearchTree:
    """
    Standard Binary Search Tree.

    Supports insert, delete, search, and in-order traversal.
    No balancing is performed — this serves as a baseline.
    """

    def __init__(self) -> None:
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self.root is None

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: int) -> Optional[BSTNode]:
        """Return the node with the given key, or None if not found."""
        node = self.root
        while node is not None:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def contains(self, key: int) -> bool:
        return self.search(key) is not None

    def minimum(self, node: Optional[BSTNode] = None) -> Optional[BSTNode]:
        if node is None:
            node = self.root
        if node is None:
            return None
        while node.left is not None:
            node = node.left
        return node

    def maximum(self, node: Optional[BSTNode] = None) -> Optional[BSTNode]:
        if node is None:
            node = self.root
        if node is None:
            return None
        while node.right is not None:
            node = node.right
        return node

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def inorder(self, node: Optional[BSTNode] = ...) -> Generator[BSTNode, None, None]:
        """In-order traversal yielding nodes in sorted key order."""
        if node is ...:
            node = self.root
        if node is not None:
            yield from self.inorder(node.left)
            yield node
            yield from self.inorder(node.right)

    def to_list(self) -> list[int]:
        return [n.key for n in self.inorder()]

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------

    def insert(self, key: int) -> BSTNode:
        """Insert a key and return the new node."""
        new_node = BSTNode(key=key)
        parent = None
        current = self.root

        while current is not None:
            parent = current
            if key < current.key:
                current = current.left
            else:
                current = current.right

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        return new_node

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def _transplant(self, u: BSTNode, v: Optional[BSTNode]) -> None:
        """Replace subtree rooted at u with subtree rooted at v."""
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def delete(self, key: int) -> bool:
        """Delete the node with the given key. Returns True if found and deleted."""
        z = self.search(key)
        if z is None:
            return False

        if z.left is None:
            self._transplant(z, z.right)
        elif z.right is None:
            self._transplant(z, z.left)
        else:
            # Find in-order successor
            y = self.minimum(z.right)
            if y.parent is not z:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y

        self._size -= 1
        return True

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def height(self, node: Optional[BSTNode] = ...) -> int:
        """Return the height of the tree (or subtree)."""
        if node is ...:
            node = self.root
        if node is None:
            return -1
        return 1 + max(self.height(node.left), self.height(node.right))
