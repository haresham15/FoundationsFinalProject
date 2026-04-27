"""
Red-Black Tree Implementation
==============================
A self-balancing binary search tree where every node is colored red or black.
Guarantees O(log n) time for insert, delete, and search operations.

Properties:
    1. Every node is either red or black.
    2. The root is black.
    3. Every leaf (NIL sentinel) is black.
    4. If a node is red, both its children are black.
    5. All paths from any node to its descendant NIL leaves contain the
       same number of black nodes (uniform black-height).

References:
    - Cormen, Leiserson, Rivest, Stein (CLRS), Chapter 13
    - Ali Alilooee's Red-Black Tree presentation
"""

from __future__ import annotations
from enum import IntEnum
from typing import Generator, Optional


class Color(IntEnum):
    """Node color constants."""
    RED = 0
    BLACK = 1


class Node:
    """
    A node in a Red-Black Tree.

    Attributes:
        key: The value stored in this node.
        color: RED or BLACK.
        left: Left child (or the sentinel NIL).
        right: Right child (or the sentinel NIL).
        parent: Parent node (or the sentinel NIL for the root).
    """

    __slots__ = ("key", "color", "left", "right", "parent")

    def __init__(
        self,
        key: int,
        color: Color = Color.RED,
        left: Optional[Node] = None,
        right: Optional[Node] = None,
        parent: Optional[Node] = None,
    ) -> None:
        self.key = key
        self.color = color
        self.left = left
        self.right = right
        self.parent = parent

    def __repr__(self) -> str:
        c = "R" if self.color == Color.RED else "B"
        return f"Node({self.key}, {c})"


class RedBlackTree:
    """
    Red-Black Tree with insert, delete, search, and traversal operations.

    Uses a shared sentinel NIL node to represent all external leaves,
    simplifying boundary-condition handling in rotations and fixups.
    """

    def __init__(self) -> None:
        # Sentinel NIL node — shared by all leaves and used as the root's parent
        self.NIL: Node = Node(key=0, color=Color.BLACK)
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.NIL.parent = self.NIL
        self.root: Node = self.NIL
        self._size: int = 0

    # ------------------------------------------------------------------
    # Public Properties
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        """Return the number of nodes in the tree."""
        return self._size

    @property
    def is_empty(self) -> bool:
        """Return True if the tree has no nodes."""
        return self.root is self.NIL

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: int) -> Node:
        """
        Search for a node with the given key.

        Returns:
            The Node if found, otherwise self.NIL.
        """
        node = self.root
        while node is not self.NIL:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return self.NIL

    def contains(self, key: int) -> bool:
        """Return True if the key exists in the tree."""
        return self.search(key) is not self.NIL

    def minimum(self, node: Optional[Node] = None) -> Node:
        """Return the node with the smallest key in the subtree rooted at *node*."""
        if node is None:
            node = self.root
        while node.left is not self.NIL:
            node = node.left
        return node

    def maximum(self, node: Optional[Node] = None) -> Node:
        """Return the node with the largest key in the subtree rooted at *node*."""
        if node is None:
            node = self.root
        while node.right is not self.NIL:
            node = node.right
        return node

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------

    def inorder(self, node: Optional[Node] = None) -> Generator[Node, None, None]:
        """In-order traversal (sorted order)."""
        if node is None:
            node = self.root
        if node is not self.NIL:
            yield from self.inorder(node.left)
            yield node
            yield from self.inorder(node.right)

    def preorder(self, node: Optional[Node] = None) -> Generator[Node, None, None]:
        """Pre-order traversal (root first)."""
        if node is None:
            node = self.root
        if node is not self.NIL:
            yield node
            yield from self.preorder(node.left)
            yield from self.preorder(node.right)

    def postorder(self, node: Optional[Node] = None) -> Generator[Node, None, None]:
        """Post-order traversal (root last)."""
        if node is None:
            node = self.root
        if node is not self.NIL:
            yield from self.postorder(node.left)
            yield from self.postorder(node.right)
            yield node

    def level_order(self) -> Generator[list[Node], None, None]:
        """Level-order (BFS) traversal. Yields one list of nodes per level."""
        if self.root is self.NIL:
            return
        queue: list[Node] = [self.root]
        while queue:
            yield list(queue)
            next_level: list[Node] = []
            for n in queue:
                if n.left is not self.NIL:
                    next_level.append(n.left)
                if n.right is not self.NIL:
                    next_level.append(n.right)
            queue = next_level

    # ------------------------------------------------------------------
    # Rotations
    # ------------------------------------------------------------------

    def _left_rotate(self, x: Node) -> None:
        """
        Left-rotate the subtree rooted at node *x*.

        Before:          After:
            x               y
           / \\             / \\
          a   y           x   c
             / \\         / \\
            b   c       a   b
        """
        y = x.right
        # Turn y's left subtree into x's right subtree
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        # Link x's parent to y
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        # Put x on y's left
        y.left = x
        x.parent = y

    def _right_rotate(self, y: Node) -> None:
        """
        Right-rotate the subtree rooted at node *y*.

        Before:          After:
            y               x
           / \\             / \\
          x   c           a   y
         / \\                 / \\
        a   b               b   c
        """
        x = y.left
        # Turn x's right subtree into y's left subtree
        y.left = x.right
        if x.right is not self.NIL:
            x.right.parent = y
        # Link y's parent to x
        x.parent = y.parent
        if y.parent is self.NIL:
            self.root = x
        elif y is y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        # Put y on x's right
        x.right = y
        y.parent = x

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------

    def insert(self, key: int) -> Node:
        """
        Insert a new key into the Red-Black Tree.

        The new node is placed according to BST ordering and colored RED.
        Then _insert_fixup restores the Red-Black properties.

        Returns:
            The newly inserted Node.
        """
        z = Node(key=key, color=Color.RED, left=self.NIL, right=self.NIL, parent=self.NIL)

        # Standard BST insert — find the correct parent
        y = self.NIL
        x = self.root
        while x is not self.NIL:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y

        if y is self.NIL:
            self.root = z        # Tree was empty
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z

        self._size += 1
        self._insert_fixup(z)
        return z

    def _insert_fixup(self, z: Node) -> None:
        """
        Restore Red-Black properties after inserting node *z*.

        Handles three cases (and their symmetric mirrors):
            Case I:   Uncle is red  → recolor parent, uncle, grandparent.
            Case II:  Uncle is black, z is inner child → rotate to Case III.
            Case III: Uncle is black, z is outer child → rotate grandparent, recolor.
        """
        while z.parent.color == Color.RED:
            if z.parent is z.parent.parent.left:
                # Parent is a LEFT child of grandparent
                uncle = z.parent.parent.right

                if uncle.color == Color.RED:
                    # -------- Case I: Uncle is RED --------
                    z.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    z = z.parent.parent
                else:
                    if z is z.parent.right:
                        # ---- Case II: z is RIGHT child (inner) ----
                        z = z.parent
                        self._left_rotate(z)
                    # ---- Case III: z is LEFT child (outer) ----
                    z.parent.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    self._right_rotate(z.parent.parent)
            else:
                # MIRROR: Parent is a RIGHT child of grandparent
                uncle = z.parent.parent.left

                if uncle.color == Color.RED:
                    # -------- Case I (mirror) --------
                    z.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    z = z.parent.parent
                else:
                    if z is z.parent.left:
                        # ---- Case II (mirror) ----
                        z = z.parent
                        self._right_rotate(z)
                    # ---- Case III (mirror) ----
                    z.parent.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    self._left_rotate(z.parent.parent)

        # Property 2: root must always be black
        self.root.color = Color.BLACK

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def _transplant(self, u: Node, v: Node) -> None:
        """
        Replace the subtree rooted at *u* with the subtree rooted at *v*.
        """
        if u.parent is self.NIL:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def delete(self, key: int) -> bool:
        """
        Delete the node with the given key from the tree.

        Returns:
            True if the key was found and deleted, False otherwise.
        """
        z = self.search(key)
        if z is self.NIL:
            return False

        y = z
        y_original_color = y.color

        if z.left is self.NIL:
            # Case A: No left child — replace z with its right child
            x = z.right
            self._transplant(z, z.right)
        elif z.right is self.NIL:
            # Case B: No right child — replace z with its left child
            x = z.left
            self._transplant(z, z.left)
        else:
            # Case C: Two children — replace with in-order successor
            y = self.minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent is z:
                # Successor is z's direct right child
                x.parent = y   # Important even if x is NIL
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color

        self._size -= 1

        if y_original_color == Color.BLACK:
            self._delete_fixup(x)

        return True

    def _delete_fixup(self, x: Node) -> None:
        """
        Restore Red-Black properties after deletion.

        Handles four cases (and their symmetric mirrors):
            Case 1: Sibling w is red.
            Case 2: Sibling w is black, both of w's children are black.
            Case 3: Sibling w is black, w's left child is red, right is black.
            Case 4: Sibling w is black, w's right child is red.
        """
        while x is not self.root and x.color == Color.BLACK:
            if x is x.parent.left:
                w = x.parent.right  # Sibling

                if w.color == Color.RED:
                    # -------- Case 1: Sibling is RED --------
                    w.color = Color.BLACK
                    x.parent.color = Color.RED
                    self._left_rotate(x.parent)
                    w = x.parent.right

                if w.left.color == Color.BLACK and w.right.color == Color.BLACK:
                    # -------- Case 2: Both of w's children are BLACK --------
                    w.color = Color.RED
                    x = x.parent
                else:
                    if w.right.color == Color.BLACK:
                        # ---- Case 3: w's right child is BLACK ----
                        w.left.color = Color.BLACK
                        w.color = Color.RED
                        self._right_rotate(w)
                        w = x.parent.right
                    # ---- Case 4: w's right child is RED ----
                    w.color = x.parent.color
                    x.parent.color = Color.BLACK
                    w.right.color = Color.BLACK
                    self._left_rotate(x.parent)
                    x = self.root  # Terminate loop
            else:
                # MIRROR: x is a right child
                w = x.parent.left

                if w.color == Color.RED:
                    # -------- Case 1 (mirror) --------
                    w.color = Color.BLACK
                    x.parent.color = Color.RED
                    self._right_rotate(x.parent)
                    w = x.parent.left

                if w.right.color == Color.BLACK and w.left.color == Color.BLACK:
                    # -------- Case 2 (mirror) --------
                    w.color = Color.RED
                    x = x.parent
                else:
                    if w.left.color == Color.BLACK:
                        # ---- Case 3 (mirror) ----
                        w.right.color = Color.BLACK
                        w.color = Color.RED
                        self._left_rotate(w)
                        w = x.parent.left
                    # ---- Case 4 (mirror) ----
                    w.color = x.parent.color
                    x.parent.color = Color.BLACK
                    w.left.color = Color.BLACK
                    self._right_rotate(x.parent)
                    x = self.root

        x.color = Color.BLACK

    # ------------------------------------------------------------------
    # Tree Metrics
    # ------------------------------------------------------------------

    def height(self, node: Optional[Node] = None) -> int:
        """Return the height of the tree (or subtree rooted at *node*)."""
        if node is None:
            node = self.root
        if node is self.NIL:
            return -1
        return 1 + max(self.height(node.left), self.height(node.right))

    def black_height(self, node: Optional[Node] = None) -> int:
        """
        Return the black-height of the tree (or subtree rooted at *node*).

        The black-height is the number of black nodes on any path from the
        given node down to a NIL leaf (not counting the node itself).
        """
        if node is None:
            node = self.root
        if node is self.NIL:
            return 0
        # Follow the left spine (all paths have the same black-height)
        left_bh = self.black_height(node.left)
        return left_bh + (1 if node.left.color == Color.BLACK else 0)

    # ------------------------------------------------------------------
    # Validation (for testing)
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate all five Red-Black Tree properties.

        Raises AssertionError with a descriptive message if any property
        is violated. Returns True if valid.
        """
        if self.root is self.NIL:
            return True

        # Property 2: Root is black
        assert self.root.color == Color.BLACK, \
            f"Property 2 violated: root {self.root} is RED"

        # Property 1, 3, 4, 5: Walk the entire tree
        self._validate_subtree(self.root)
        return True

    def _validate_subtree(self, node: Node) -> int:
        """
        Recursively validate properties and return the black-height of *node*.

        Returns:
            The black-height (number of black nodes from node to any leaf).
        """
        if node is self.NIL:
            # Property 3: NIL leaves are black
            assert node.color == Color.BLACK, "Property 3 violated: NIL is not BLACK"
            return 1

        # Property 1: Node is red or black (enforced by the Color enum)

        # Property 4: Red node must have black children
        if node.color == Color.RED:
            assert node.left.color == Color.BLACK, \
                f"Property 4 violated: RED node {node} has RED left child {node.left}"
            assert node.right.color == Color.BLACK, \
                f"Property 4 violated: RED node {node} has RED right child {node.right}"

        # Check BST ordering
        if node.left is not self.NIL:
            assert node.left.key <= node.key, \
                f"BST violation: {node.left.key} > {node.key}"
        if node.right is not self.NIL:
            assert node.right.key >= node.key, \
                f"BST violation: {node.right.key} < {node.key}"

        # Property 5: Equal black-height on all paths
        left_bh = self._validate_subtree(node.left)
        right_bh = self._validate_subtree(node.right)
        assert left_bh == right_bh, \
            f"Property 5 violated at {node}: left bh={left_bh}, right bh={right_bh}"

        return left_bh + (1 if node.color == Color.BLACK else 0)

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a multi-line string visualization of the tree."""
        if self.root is self.NIL:
            return "(empty tree)"
        lines: list[str] = []
        self._build_str(self.root, "", True, lines)
        return "\n".join(lines)

    def _build_str(self, node: Node, prefix: str, is_right: bool, lines: list[str]) -> None:
        """Recursively build a string representation of the tree."""
        if node is self.NIL:
            return
        connector = "└── " if is_right else "┌── "
        color_label = "R" if node.color == Color.RED else "B"
        lines.append(f"{prefix}{connector}({node.key},{color_label})")
        new_prefix = prefix + ("    " if is_right else "│   ")
        self._build_str(node.right, new_prefix, True, lines) if node.right is not self.NIL else None
        self._build_str(node.left, new_prefix, False, lines) if node.left is not self.NIL else None

    def to_list(self) -> list[int]:
        """Return all keys in sorted order."""
        return [node.key for node in self.inorder()]
