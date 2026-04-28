class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if not self.root:
            self.root = Node(key)
            return
        curr = self.root
        while True:
            if key < curr.key:
                if curr.left is None:
                    curr.left = Node(key)
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = Node(key)
                    break
                curr = curr.right

    def inorder(self, node=None, res=None):
        if res is None:
            res = []
            node = self.root
        if node:
            self.inorder(node.left, res)
            res.append(node.key)
            self.inorder(node.right, res)
        return res
