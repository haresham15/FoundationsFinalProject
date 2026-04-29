# Red-Black Tree Project

This is my final project for Foundations of Computer Science. I implemented a Red-Black Tree from scratch in Python.

# Files
- `src/rbt.py`: The main Red-Black Tree implementation.
- `src/bst.py`: A standard Binary Search Tree for comparison.
- `src/avl.py`: An AVL Tree for comparison.
- `benchmarks/benchmark.py`: Script to measure insertion times.
- `visualization/index.html`: A very basic HTML page to visualize trees.
- `docs/report.md`: My write-up explaining the data structure.

# How to Run

To run the benchmarks:
python benchmarks/benchmark.py

To view the visualization: 
open `visualization/index.html`

## Properties of a Red Black Tree
1. Every node is red or black.
2. The root is black.
3. Every leaf is black.
4. If a node is red, its children are black.
5. All paths from a node to its leaves have the same number of black nodes.
