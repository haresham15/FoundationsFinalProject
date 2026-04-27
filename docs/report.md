# Red-Black Tree — Implementation Report

## 1. Introduction

A Red-Black Tree (RBT) is a self-balancing binary search tree where each node carries an additional bit of information: its **color** (red or black). By enforcing a set of coloring constraints, the tree guarantees that no path from the root to a leaf is more than twice as long as any other, ensuring **O(log n)** worst-case time for insertion, deletion, and search.

This report documents the design, implementation, and analysis of a Red-Black Tree built from scratch in Python, alongside a comparative study with AVL Trees and standard (unbalanced) Binary Search Trees.

---

## 2. Red-Black Tree Properties

The five invariants that define a valid Red-Black Tree:

| # | Property | Purpose |
|---|----------|---------|
| 1 | Every node is red or black | Foundation for the coloring scheme |
| 2 | The root is black | Simplifies fixup termination |
| 3 | Every NIL leaf is black | Uniform treatment of boundaries |
| 4 | Red nodes have only black children | Prevents consecutive red nodes |
| 5 | All root-to-leaf paths have equal black-height | Ensures balanced depth |

### Black-Height

The **black-height** `bh(x)` of a node `x` is the number of black nodes on any simple path from `x` down to a NIL leaf (not counting `x` itself). Property 5 guarantees this is well-defined.

### Height Theorem

For a Red-Black Tree with `n` internal nodes:

```
h ≤ 2 · log₂(n + 1)
```

**Proof sketch:**
- By Property 4, at least half of all nodes on any root-to-leaf path are black.
- Therefore, `bh(root) ≥ h/2`.
- The subtree rooted at any node `x` has at least `2^bh(x) - 1` internal nodes.
- Combining: `n ≥ 2^(h/2) - 1`, which gives `h ≤ 2 · log₂(n + 1)`.

---

## 3. Implementation Details

### 3.1 Design Decisions

#### Sentinel NIL Node

We use a **shared sentinel NIL node** rather than `None` for leaf pointers. This eliminates null-checking throughout the rotation and fixup code:

```python
self.NIL = Node(key=0, color=Color.BLACK)
self.NIL.left = self.NIL
self.NIL.right = self.NIL
self.NIL.parent = self.NIL
self.root = self.NIL
```

Every leaf pointer and the root's parent pointer reference this single sentinel, which is always black (satisfying Property 3).

#### Color Representation

Colors are represented as an `IntEnum` for clarity and type safety:

```python
class Color(IntEnum):
    RED = 0
    BLACK = 1
```

#### Node Structure

Each node stores:
- `key` — the integer value
- `color` — RED or BLACK
- `left`, `right`, `parent` — child/parent references (or NIL)

Using `__slots__` for memory efficiency.

### 3.2 Rotations

Rotations are the fundamental restructuring operation. They preserve BST ordering while changing the tree's shape.

**Left Rotation** on node `x`:
```
    x               y
   / \             / \
  a   y    →     x   c
     / \        / \
    b   c      a   b
```

**Right Rotation** is the symmetric inverse.

Both operations run in **O(1)** time — they only update a constant number of pointers.

### 3.3 Insertion

Insertion follows two phases:

1. **BST Insert**: Walk down the tree to find the correct position and attach the new node as a **red** leaf.
2. **Fixup**: Restore RBT properties by walking up toward the root, handling three cases:

#### Case I — Uncle is Red (Recoloring)
```
         G(B)                G(R)
        / \                 / \
      P(R) U(R)    →     P(B) U(B)
      /                  /
    Z(R)               Z(R)
```
Recolor parent and uncle to black, grandparent to red.[d Push the "problem" up by setting `z = G`.

#### Case II — Uncle is Black, Z is Inner Child (Rotate to Case III)
```
      G(B)              G(B)
     / \               / \
   P(R) U(B)   →    Z(R) U(B)
     \               /
    Z(R)           P(R)
```
Left-rotate on `P`, which transforms into Case III.

#### Case III — Uncle is Black, Z is Outer Child (Rotate + Recolor)
```
        G(B)              P(B)
       / \               / \
     P(R) U(B)   →    Z(R) G(R)
     /                       \
   Z(R)                     U(B)
```
Right-rotate on `G`, recolor `P` black and `G` red.

Each symmetric (mirror) case handles the situation where the parent is a right child.

### 3.4 Deletion

Deletion is more complex and uses three components:

1. **Transplant**: Replace one subtree with another.
2. **BST Delete**: Handle three sub-cases (no left child, no right child, two children with successor replacement).
3. **Fixup**: If the removed or moved node was black, restore properties via four cases:

| Case | Condition | Action |
|------|-----------|--------|
| 1 | Sibling is red | Rotate, recolor → converts to cases 2–4 |
| 2 | Sibling is black, both children black | Recolor sibling red, move up |
| 3 | Sibling is black, far child black | Rotate sibling, recolor → case 4 |
| 4 | Sibling is black, far child red | Rotate parent, recolor → done |

### 3.5 Validation

The `validate()` method programmatically checks all five properties:

```python
def validate(self) -> bool:
    # Property 2: Root is black
    assert self.root.color == Color.BLACK
    # Walk tree checking Properties 1, 3, 4, 5
    self._validate_subtree(self.root)
    return True
```

The recursive `_validate_subtree` returns the black-height at each node and asserts:
- NIL leaves are black (Property 3)
- Red nodes have black children (Property 4)
- Left and right black-heights are equal (Property 5)
- BST ordering is maintained

---

## 4. Complexity Analysis

### Time Complexity

| Operation | Worst Case | Amortized |
|-----------|:----------:|:---------:|
| Search    | O(log n)   | O(log n)  |
| Insert    | O(log n)   | O(log n)  |
| Delete    | O(log n)   | O(log n)  |
| Min/Max   | O(log n)   | O(log n)  |
| Traversal | O(n)       | O(n)      |

### Space Complexity

- **O(n)** for storing n nodes.
- **O(1)** additional space per operation (rotations use constant pointer updates).
- **O(log n)** stack space for recursive traversals.

### Rotation Counts

- **Insert**: At most **2 rotations** and O(log n) recolorings.
- **Delete**: At most **3 rotations** and O(log n) recolorings.

This is a key advantage over AVL trees, which may perform O(log n) rotations during deletion.

---

## 5. Comparison: RBT vs AVL vs BST

| Property | Red-Black Tree | AVL Tree | BST (unbalanced) |
|----------|:-:|:-:|:-:|
| Height guarantee | 2·log₂(n+1) | 1.44·log₂(n+2) | O(n) worst case |
| Insert rotations | ≤ 2 | O(log n) | 0 (no balancing) |
| Delete rotations | ≤ 3 | O(log n) | 0 (no balancing) |
| Insert time | O(log n) | O(log n) | O(n) worst |
| Search time | O(log n) | O(log n) | O(n) worst |
| Delete time | O(log n) | O(log n) | O(n) worst |
| Balance strictness | Relaxed | Strict | None |

### Key Trade-offs

1. **RBT vs AVL**: AVL trees maintain stricter balance (lower height), making searches slightly faster. However, RBT insertion and deletion are faster because they require fewer rotations. This makes RBTs preferred for **write-heavy** workloads.

2. **RBT vs BST**: An unbalanced BST degrades to a linked list with sorted input (height = n). RBTs guarantee logarithmic height regardless of insertion order, making them far superior for any non-random workload.

3. **Real-world usage**: RBTs are used in Linux kernel's CFS scheduler, Java's `TreeMap`, C++ `std::map`, and many database indexing systems.

---

## 6. Testing Summary

The test suite contains **50+ test cases** organized as:

| Category | Tests | Coverage |
|----------|:-----:|----------|
| Property validation | 7 | All 5 RBT properties after insert/delete |
| Insertion | 6 | Single, multiple, duplicates, ascending, descending |
| Fixup cases | 4 | Case I, II, III, and mirror cases |
| Deletion | 8 | Leaf, 1-child, 2-children, root, all, random order |
| Search | 6 | Hit, miss, empty tree, min, max, contains |
| Rotations | 2 | Left/right preserve BST ordering |
| Traversals | 5 | In-order, pre-order, post-order, level-order |
| Metrics | 6 | Height, black-height, size tracking, height bound |
| Integration | 6 | Insert-search-all, delete-all, interleaved, stress 10K |

### Stress Testing

The most rigorous test performs **10,000 random operations** (60% inserts, 40% deletes) and validates all RBT properties after each operation, ensuring correctness under heavy, randomized workloads.

---

## 7. Visualization

An interactive web-based visualizer is included (`visualization/`) built with Next.js and React, featuring:

- **Canvas rendering** with smooth animated transitions
- **Red/black node coloring** with glow effects
- **Step-by-step operations**: insert, delete, search with path highlighting
- **Traversal animation**: in-order, pre-order, post-order with sequential node highlighting
- **Pan support**: drag to navigate large trees
- **Stats display**: real-time node count, height, and black-height
- **Dark glassmorphic design** with Inter typography

---

## 8. Conclusion

This implementation demonstrates:

1. **Correctness**: All five RBT properties are rigorously validated, with the `validate()` method serving as the foundation of the test suite.
2. **Completeness**: Insert, delete, search, traversals, and tree metrics are all implemented.
3. **Efficiency**: The height bound h ≤ 2·log₂(n+1) is empirically verified up to n=100,000.
4. **Practical comparison**: Benchmarks quantify the real-world performance differences between RBT, AVL, and BST across multiple input distributions.

The Red-Black Tree stands as one of the most practical self-balancing BSTs — the relaxed balancing constraints (compared to AVL) reduce rotation overhead during modifications while still guaranteeing O(log n) operations for all inputs.
