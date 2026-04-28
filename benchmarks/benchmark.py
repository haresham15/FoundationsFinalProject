import time
import random
from src.rbt import RedBlackTree
from src.avl import AVLTree
from src.bst import BinarySearchTree

def benchmark():
    sizes = [1000, 5000, 10000]
    trees = [
        ("BST", BinarySearchTree),
        ("AVL", AVLTree),
        ("RBT", RedBlackTree)
    ]

    print("Performance Benchmark (Insertion Time in seconds)")
    print("-" * 50)
    
    for size in sizes:
        print(f"Data Size: {size}")
        data = list(range(size))
        random.shuffle(data)
        
        for name, TreeClass in trees:
            tree = TreeClass()
            start_time = time.time()
            for key in data:
                tree.insert(key)
            end_time = time.time()
            print(f"  {name}: {end_time - start_time:.5f}s")
        print("-" * 50)

if __name__ == "__main__":
    benchmark()
