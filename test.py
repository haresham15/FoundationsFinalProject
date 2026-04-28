from src.rbt import RedBlackTree

def run_tests():
    tree = RedBlackTree()
    
    # Test Insertion
    print("Testing Insertion...")
    for key in [10, 20, 30, 15, 25]:
        tree.insert(key)
    
    res = tree.inorder()
    print("Inorder traversal:", res)
    assert res == [10, 15, 20, 25, 30], "Insertion or inorder traversal failed!"
    
    # Test Search
    print("Testing Search...")
    node = tree.search(20)
    assert node is not None and node.key == 20, "Search for 20 failed!"
    
    node = tree.search(99)
    assert node is None, "Search for 99 should fail!"
    
    # Test Deletion
    print("Testing Deletion...")
    tree.delete(20)
    res = tree.inorder()
    print("Inorder traversal after deleting 20:", res)
    assert res == [10, 15, 25, 30], "Deletion failed!"
    
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
