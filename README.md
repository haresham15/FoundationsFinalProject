# Red-Black Tree Implementation & Performance Analysis

A comprehensive implementation of a **Red-Black Tree** data structure in Python, with a complete test suite, comparative performance benchmarks against AVL and Binary Search Trees, an interactive web-based visualizer, and detailed documentation.

## 📁 Project Structure

```
FoundationsFinalProject/
├── src/                        # Core data structure implementations
│   ├── rbt.py                  # Red-Black Tree (primary deliverable)
│   ├── bst.py                  # Binary Search Tree (baseline)
│   ├── avl.py                  # AVL Tree (comparison)
│   └── utils.py                # Shared helpers
├── tests/                      # Comprehensive test suite
│   ├── test_rbt.py             # RBT unit + integration tests
│   ├── test_bst.py             # BST tests
│   └── test_avl.py             # AVL tests
├── benchmarks/                 # Performance analysis
│   ├── benchmark.py            # Benchmark runner + chart generator
│   └── results/                # Generated charts and CSV data
├── visualization/              # Interactive web visualizer (Next.js)
│   ├── src/                    # Frontend source code
│   │   ├── app/                # Next.js App Router (page.js, globals.css)
│   │   └── lib/                # Shared logic (rbt.js)
├── docs/
│   └── report.md               # Implementation report
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run only RBT tests
pytest tests/test_rbt.py -v
```

### Run Benchmarks

```bash
# Run performance benchmarks (generates charts in benchmarks/results/)
python -m benchmarks.benchmark
```

### Launch Visualizer

The visualizer is built with Next.js. To start the development server:

```bash
cd visualization
npm install
npm run dev
```

Then open `http://localhost:3000` in any modern web browser.

## 🌳 Red-Black Tree Properties

A Red-Black Tree is a self-balancing binary search tree satisfying five properties:

1. Every node is either **red** or **black**.
2. The **root** is always black.
3. Every leaf (**NIL** sentinel) is black.
4. If a node is **red**, both its children must be **black** (no two consecutive red nodes).
5. All paths from any node to its descendant NIL leaves contain the **same number of black nodes** (uniform black-height).

These properties guarantee a maximum height of **h ≤ 2·log₂(n+1)**, ensuring O(log n) operations.

## 🔧 Operations

| Operation | Time Complexity | Description |
|-----------|:-:|-------------|
| Insert | O(log n) | Insert with red coloring, then fixup rotations/recoloring |
| Delete | O(log n) | Delete with transplant, then fixup |
| Search | O(log n) | Standard BST search |
| Min/Max | O(log n) | Walk left/right spine |
| Traversals | O(n) | In-order, pre-order, post-order, level-order |

## 📊 Performance Analysis

Benchmarks compare **Red-Black Tree**, **AVL Tree**, and **Binary Search Tree** across:
- **7 input sizes**: 100 → 100,000
- **3 distributions**: random, sorted (ascending), reverse sorted
- **3 operations**: insertion, search, deletion

Key findings:
- **BST degrades to O(n)** with sorted input (height ≈ n)
- **RBT and AVL maintain O(log n)** regardless of input distribution
- **AVL has slightly lower height** (~1.44·log n) but **RBT has lower insertion overhead** due to fewer rotations on average

## 🎨 Visualization

The interactive web visualizer allows you to:
- **Insert** nodes and watch the tree rebalance with animated rotations
- **Delete** nodes with visual fixup
- **Search** with path highlighting
- View **traversal animations** (in-order, pre-order, post-order)
- **Pan** the canvas by dragging
- Generate **random trees** or load a **sample tree**
- Track real-time **stats**: node count, height, black-height

## 🧪 Testing

The test suite includes **50+ tests** covering:

- **Property validation**: All 5 RBT properties verified after every operation
- **Fixup case coverage**: Specifically triggers Cases I, II, III and their mirrors
- **Edge cases**: Empty tree, single node, duplicates, root deletion
- **Stress tests**: 10,000 random insert/delete/search operations with validation
- **Height guarantee**: Verifies h ≤ 2·log₂(n+1) for sorted input up to n=5,000

## 📝 References

- Cormen, Leiserson, Rivest, Stein — *Introduction to Algorithms* (CLRS), Chapter 13
- Ali Alilooee — Red-Black Tree Presentation
