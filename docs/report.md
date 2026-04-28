# Red-Black Tree Implementation Report

## Introduction
For this project, I implemented a Red-Black Tree in Python. A Red-Black Tree is a self-balancing binary search tree. It uses node colors (red or black) to keep the tree balanced so that operations like insert, delete, and search take O(log n) time.

## Data Structure Design
I created a `Node` class that stores the key, the color, and pointers to the left child, right child, and parent.
The `RedBlackTree` class handles all the logic. I used a shared `NIL` node instead of `None` to make it easier to handle leaf nodes and avoid null pointer errors when rotating.

## Insertion
When inserting, the new node is placed just like a normal Binary Search Tree and colored Red. Then, a fixup function is called to make sure the red-black properties aren't violated. There are three main cases handled in the fixup depending on the color of the "uncle" node.

## Deletion
Deletion is similar to a regular BST where we might have to replace a node with its successor. After removing the node, if the removed node was Black, we have to call a fixup function to restore the black-height property.

## Performance Analysis
I wrote a basic benchmark script that tests the insertion time for 1,000, 5,000, and 10,000 elements.
Compared to a regular Binary Search Tree, the Red-Black tree is much faster when inserting sorted data because it stays balanced. The AVL tree is also balanced but does more rotations than the Red-Black tree, making the RBT slightly faster for insertions.

## Testing
I wrote a `test.py` script that does some basic inserts and deletes and verifies that the `inorder` traversal returns the keys in sorted order. It prints out confirmation when the tests pass.

## Conclusion
Implementing this tree was challenging, especially the delete fixup cases, but it works and successfully keeps the tree balanced in O(log n) time.
