from src.rbt import RedBlackTree

def test_insertion_and_search():
    tree = RedBlackTree()
    print("Testing Insertion...")
    keys_to_insert = [10, 20, 30, 15, 25]
    for key in keys_to_insert:
        tree.insert(key)
    res = tree.inorder()
    print("Inorder traversal:", res)
    assert res == [10, 15, 20, 25, 30], "Insertion or inorder traversal failed!"
    
    print("Testing Search...")
    node = tree.search(20)
    assert node is not None and node.key == 20, "Search for 20 failed!"
    node = tree.search(99)
    assert node is None, "Search for 99 should fail!"
    print("Insertion and Search tests passed.")

def test_deletion():
    tree = RedBlackTree()
    for key in [10, 20, 30, 15, 25]:
        tree.insert(key)
    print("Testing Deletion...")
    tree.delete(20)
    res = tree.inorder()
    print("Inorder traversal after deleting 20:", res)
    assert res == [10, 15, 25, 30], "Deletion failed!"
    print("Deletion test passed.")

if __name__ == "__main__":
    print("--- Running Red-Black Tree Tests ---")
    test_insertion_and_search()
    test_deletion()
    print("--- All Tests Passed Successfully! ---")
