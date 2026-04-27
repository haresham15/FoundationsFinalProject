"""
AVL Tree Implementation
========================
A self-balancing binary search tree where the heights of the two child
subtrees of any node differ by at most one. Used for performance
comparison against the Red-Black Tree.

All operations are O(log n).
"""

from __future__ import annotations
from typing import Generator, Optional


class AVLNode:
    """A node in an AVL Tree."""

    __slots__ = ("key", "left", "right", "parent", "height")

    def __init__(
        self,
        key: int,
        left: Optional[AVLNode] = None,
        right: Optional[AVLNode] = None,
        parent: Optional[AVLNode] = None,
    ) -> None:
        self.key = key
        self.left = left
        self.right = right
        self.parent = parent
        self.height: int = 0

    def __repr__(self) -> str:
        return f"AVLNode({self.key}, h={self.height})"


class AVLTree:
    """
    AVL Tree with insert, delete, search, and traversal.

    Maintains the AVL balance invariant: for every node, the height
    difference between left and right subtrees is at most 1.
    """

    def __init__(self) -> None:
        self.root: Optional[AVLNode] = None
        self._size: int = 0

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self.root is None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_height(node: Optional[AVLNode]) -> int:
        return node.height if node is not None else -1

    @staticmethod
    def _get_balance(node: Optional[AVLNode]) -> int:
        if node is None:
            return 0
        return AVLTree._get_height(node.left) - AVLTree._get_height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right),
        )

    # ------------------------------------------------------------------
    # Rotations
    # ------------------------------------------------------------------

    def _left_rotate(self, x: AVLNode) -> AVLNode:
        y = x.right
        b = y.left

        y.left = x
        x.right = b

        y.parent = x.parent
        x.parent = y
        if b is not None:
            b.parent = x

        if y.parent is None:
            self.root = y
        elif y.parent.left is x:
            y.parent.left = y
        else:
            y.parent.right = y

        self._update_height(x)
        self._update_height(y)
        return y

    def _right_rotate(self, y: AVLNode) -> AVLNode:
        x = y.left
        b = x.right

        x.right = y
        y.left = b

        x.parent = y.parent
        y.parent = x
        if b is not None:
            b.parent = y

        if x.parent is None:
            self.root = x
        elif x.parent.left is y:
            x.parent.left = x
        else:
            x.parent.right = x

        self._update_height(y)
        self._update_height(x)
        return x

    # ------------------------------------------------------------------
    # Rebalancing
    # ------------------------------------------------------------------

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """Rebalance the subtree rooted at *node* and return the new root."""
        self._update_height(node)
        balance = self._get_balance(node)

        if balance > 1:
            # Left-heavy
            if self._get_balance(node.left) < 0:
                # Left-Right case
                self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1:
            # Right-heavy
            if self._get_balance(node.right) > 0:
                # Right-Left case
                self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: int) -> Optional[AVLNode]:
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

    def minimum(self, node: Optional[AVLNode] = None) -> Optional[AVLNode]:
        if node is None:
            node = self.root
        if node is None:
            return None
        while node.left is not None:
            node = node.left
        return node

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def inorder(self, node: Optional[AVLNode] = ...) -> Generator[AVLNode, None, None]:
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

    def insert(self, key: int) -> None:
        """Insert a key into the AVL tree."""
        if self.root is None:
            self.root = AVLNode(key=key)
            self._size += 1
            return

        # BST insert
        parent = None
        current = self.root
        while current is not None:
            parent = current
            if key < current.key:
                current = current.left
            else:
                current = current.right

        new_node = AVLNode(key=key, parent=parent)
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1

        # Walk back up and rebalance
        node = parent
        while node is not None:
            node = self._rebalance(node)
            node = node.parent

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete(self, key: int) -> bool:
        """Delete the node with the given key. Returns True if found."""
        node = self.search(key)
        if node is None:
            return False

        self._delete_node(node)
        self._size -= 1
        return True

    def _delete_node(self, z: AVLNode) -> None:
        """Remove node z from the tree and rebalance."""
        if z.left is None and z.right is None:
            # Leaf node
            rebalance_start = z.parent
            self._transplant(z, None)
        elif z.left is None:
            rebalance_start = z.parent
            self._transplant(z, z.right)
        elif z.right is None:
            rebalance_start = z.parent
            self._transplant(z, z.left)
        else:
            # Two children: find in-order successor
            successor = self.minimum(z.right)
            if successor.parent is not z:
                rebalance_start = successor.parent
                self._transplant(successor, successor.right)
                successor.right = z.right
                successor.right.parent = successor
            else:
                rebalance_start = successor
            self._transplant(z, successor)
            successor.left = z.left
            successor.left.parent = successor

        # Rebalance from the affected node upward
        node = rebalance_start
        while node is not None:
            node = self._rebalance(node)
            node = node.parent

    def _transplant(self, u: AVLNode, v: Optional[AVLNode]) -> None:
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def height(self, node: Optional[AVLNode] = ...) -> int:
        if node is ...:
            node = self.root
        if node is None:
            return -1
        return node.height
