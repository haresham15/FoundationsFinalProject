"""
Performance Benchmark
======================
Measures and compares the performance of Red-Black Tree, AVL Tree, and
Binary Search Tree across multiple input sizes and distributions.

Generates:
    - benchmark_results.csv          (raw timing data)
    - insertion_comparison.png       (insertion time chart)
    - deletion_comparison.png        (deletion time chart)
    - search_comparison.png          (search time chart)
    - height_comparison.png          (tree height chart)

Usage:
    python -m benchmarks.benchmark
"""

from __future__ import annotations

import csv
import math
import os
import random
import sys
import time
from pathlib import Path

# Increase recursion limit for pathological BST cases (up to 100k height)
sys.setrecursionlimit(200_000)

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for file output
import matplotlib.pyplot as plt
from tabulate import tabulate

from src.rbt import RedBlackTree
from src.bst import BinarySearchTree
from src.avl import AVLTree

# ======================================================================
# Configuration
# ======================================================================

SIZES = [100, 500, 1_000, 2_500, 5_000, 10_000]
DISTRIBUTIONS = ["random", "sorted", "reverse_sorted"]
NUM_RUNS = 3
RESULTS_DIR = Path(__file__).resolve().parent / "results"

# Chart styling
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",
    "axes.labelcolor": "#c9d1d9",
    "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",
    "text.color": "#c9d1d9",
    "grid.color": "#21262d",
    "legend.facecolor": "#161b22",
    "legend.edgecolor": "#30363d",
    "font.family": "sans-serif",
    "font.size": 11,
})

TREE_COLORS = {
    "RBT": "#f85149",
    "AVL": "#58a6ff",
    "BST": "#3fb950",
}

DIST_LABELS = {
    "random": "Random",
    "sorted": "Sorted (Ascending)",
    "reverse_sorted": "Reverse Sorted",
}


# ======================================================================
# Helpers
# ======================================================================

def generate_keys(n: int, distribution: str, seed: int = 42) -> list[int]:
    """Generate a list of n keys with the given distribution."""
    rng = random.Random(seed)
    if distribution == "random":
        keys = list(range(1, n + 1))
        rng.shuffle(keys)
        return keys
    elif distribution == "sorted":
        return list(range(1, n + 1))
    elif distribution == "reverse_sorted":
        return list(range(n, 0, -1))
    raise ValueError(f"Unknown distribution: {distribution}")


def time_operation(func, *args, **kwargs) -> float:
    """Time a function call in seconds using perf_counter_ns."""
    start = time.perf_counter_ns()
    func(*args, **kwargs)
    end = time.perf_counter_ns()
    return (end - start) / 1e9


# ======================================================================
# Benchmark Functions
# ======================================================================

def benchmark_insertion(tree_class, keys, tree_name, dist):
    """Time insertion of all keys into a fresh tree."""
    tree = tree_class()
    start = time.perf_counter_ns()
    for k in keys:
        tree.insert(k)
    elapsed = (time.perf_counter_ns() - start) / 1e9
    
    if tree_name == "BST" and dist in ("sorted", "reverse_sorted"):
        height = len(keys) - 1
    else:
        height = tree.height()
        
    return elapsed, height, tree


def benchmark_search(tree, keys, is_rbt=False):
    """Time searching for all keys."""
    search_keys = keys[:]
    random.Random(42).shuffle(search_keys)
    start = time.perf_counter_ns()
    for k in search_keys:
        if is_rbt:
            tree.search(k)
        else:
            tree.search(k)
    elapsed = (time.perf_counter_ns() - start) / 1e9
    return elapsed


def benchmark_deletion(tree, keys, is_rbt=False):
    """Time deleting all keys."""
    delete_keys = keys[:]
    random.Random(99).shuffle(delete_keys)
    start = time.perf_counter_ns()
    for k in delete_keys:
        tree.delete(k)
    elapsed = (time.perf_counter_ns() - start) / 1e9
    return elapsed


# ======================================================================
# Main Benchmark Runner
# ======================================================================

def run_benchmarks():
    """Run all benchmarks and collect results."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    total_configs = len(SIZES) * len(DISTRIBUTIONS)
    current = 0

    for n in SIZES:
        for dist in DISTRIBUTIONS:
            current += 1
            print(f"\n[{current}/{total_configs}] N={n:>7,}  Distribution={DIST_LABELS[dist]}")
            print("-" * 60)

            keys = generate_keys(n, dist)

            for tree_name, tree_class, is_rbt in [
                ("RBT", RedBlackTree, True),
                ("AVL", AVLTree, False),
                ("BST", BinarySearchTree, False),
            ]:
                insert_times = []
                search_times = []
                delete_times = []
                heights = []

                for run in range(NUM_RUNS):
                    # Insertion
                    elapsed, h, tree = benchmark_insertion(tree_class, keys, tree_name, dist)
                    insert_times.append(elapsed)
                    heights.append(h)

                    # Search
                    s_elapsed = benchmark_search(tree, keys, is_rbt)
                    search_times.append(s_elapsed)

                    # Deletion
                    d_elapsed = benchmark_deletion(tree, keys, is_rbt)
                    delete_times.append(d_elapsed)

                avg_insert = sum(insert_times) / NUM_RUNS
                avg_search = sum(search_times) / NUM_RUNS
                avg_delete = sum(delete_times) / NUM_RUNS
                avg_height = sum(heights) / NUM_RUNS

                print(f"  {tree_name:>3}: Insert={avg_insert:.4f}s  "
                      f"Search={avg_search:.4f}s  Delete={avg_delete:.4f}s  "
                      f"Height={avg_height:.0f}")

                results.append({
                    "tree": tree_name,
                    "n": n,
                    "distribution": dist,
                    "insert_time": avg_insert,
                    "search_time": avg_search,
                    "delete_time": avg_delete,
                    "height": avg_height,
                })

    return results


def save_csv(results: list[dict]):
    """Save results to CSV."""
    csv_path = RESULTS_DIR / "benchmark_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "tree", "n", "distribution",
            "insert_time", "search_time", "delete_time", "height",
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] Saved CSV -> {csv_path}")


def generate_charts(results: list[dict]):
    """Generate comparison charts from benchmark results."""

    # Helper: extract data for plotting
    def get_data(operation: str, dist: str, tree_name: str) -> tuple[list, list]:
        xs = []
        ys = []
        for r in results:
            if r["distribution"] == dist and r["tree"] == tree_name:
                xs.append(r["n"])
                ys.append(r[operation])
        return xs, ys

    # --- Generate one chart per operation ---
    for operation, ylabel, title_suffix in [
        ("insert_time", "Time (seconds)", "Insertion"),
        ("search_time", "Time (seconds)", "Search"),
        ("delete_time", "Time (seconds)", "Deletion"),
    ]:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
        fig.suptitle(f"{title_suffix} Performance Comparison", fontsize=16, fontweight="bold", y=1.02)

        for ax, dist in zip(axes, DISTRIBUTIONS):
            for tree_name in ["RBT", "AVL", "BST"]:
                xs, ys = get_data(operation, dist, tree_name)
                ax.plot(xs, ys, marker="o", linewidth=2, markersize=5,
                        color=TREE_COLORS[tree_name], label=tree_name)

            ax.set_title(DIST_LABELS[dist], fontsize=12)
            ax.set_xlabel("Input Size (n)")
            ax.set_xscale("log")
            ax.grid(True, alpha=0.3)
            ax.legend()

        axes[0].set_ylabel(ylabel)
        fig.tight_layout()
        filename = f"{operation.replace('_time', '')}_comparison.png"
        fig.savefig(RESULTS_DIR / filename, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"[OK] Saved chart -> {RESULTS_DIR / filename}")

    # --- Height comparison chart ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    fig.suptitle("Tree Height Comparison", fontsize=16, fontweight="bold", y=1.02)

    for ax, dist in zip(axes, DISTRIBUTIONS):
        for tree_name in ["RBT", "AVL", "BST"]:
            xs, ys = get_data("height", dist, tree_name)
            ax.plot(xs, ys, marker="s", linewidth=2, markersize=5,
                    color=TREE_COLORS[tree_name], label=tree_name)

        # Add theoretical O(log n) reference line
        ns = [r["n"] for r in results if r["distribution"] == dist and r["tree"] == "RBT"]
        log_line = [2 * math.log2(n + 1) for n in ns]
        ax.plot(ns, log_line, linestyle="--", color="#f0883e", linewidth=1.5,
                alpha=0.7, label="2·log₂(n+1)")

        ax.set_title(DIST_LABELS[dist], fontsize=12)
        ax.set_xlabel("Input Size (n)")
        ax.set_xscale("log")
        ax.grid(True, alpha=0.3)
        ax.legend()

    axes[0].set_ylabel("Height")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "height_comparison.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[OK] Saved chart -> {RESULTS_DIR / 'height_comparison.png'}")


def print_summary(results: list[dict]):
    """Print a formatted summary table."""
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)

    for dist in DISTRIBUTIONS:
        print(f"\n── {DIST_LABELS[dist]} ──")
        table = []
        for r in results:
            if r["distribution"] == dist:
                table.append([
                    r["tree"],
                    f"{r['n']:>7,}",
                    f"{r['insert_time']:.5f}",
                    f"{r['search_time']:.5f}",
                    f"{r['delete_time']:.5f}",
                    f"{r['height']:.0f}",
                ])
        print(tabulate(table,
                       headers=["Tree", "N", "Insert (s)", "Search (s)", "Delete (s)", "Height"],
                       tablefmt="rounded_grid"))


# ======================================================================
# Entry Point
# ======================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Red-Black Tree Performance Benchmark")
    print(f"  Sizes: {SIZES}")
    print(f"  Distributions: {DISTRIBUTIONS}")
    print(f"  Runs per config: {NUM_RUNS}")
    print("=" * 60)

    results = run_benchmarks()
    save_csv(results)
    generate_charts(results)
    print_summary(results)

    print("\n[DONE] Benchmark complete! Check the results/ directory for charts and data.")
