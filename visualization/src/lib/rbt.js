export const RED = 0;
export const BLACK = 1;

export class RBNode {
    constructor(key) {
        this.key = key;
        this.color = RED;
        this.left = null;
        this.right = null;
        this.parent = null;

        // Rendering state (for smooth animations)
        this.x = 0;
        this.y = 0;
        this.targetX = 0;
        this.targetY = 0;
        this.scale = 0;
        this.targetScale = 1;
        this.highlighted = false;
        this.highlightTimer = 0;
    }
}

export class RBTree {
    constructor() {
        this.NIL = new RBNode(0);
        this.NIL.color = BLACK;
        this.NIL.left = this.NIL;
        this.NIL.right = this.NIL;
        this.NIL.parent = this.NIL;
        this.root = this.NIL;
        this._size = 0;
    }

    get size() { return this._size; }
    get isEmpty() { return this.root === this.NIL; }

    // --- Rotations ---

    _leftRotate(x) {
        const y = x.right;
        x.right = y.left;
        if (y.left !== this.NIL) y.left.parent = x;
        y.parent = x.parent;
        if (x.parent === this.NIL) this.root = y;
        else if (x === x.parent.left) x.parent.left = y;
        else x.parent.right = y;
        y.left = x;
        x.parent = y;
    }

    _rightRotate(y) {
        const x = y.left;
        y.left = x.right;
        if (x.right !== this.NIL) x.right.parent = y;
        x.parent = y.parent;
        if (y.parent === this.NIL) this.root = x;
        else if (y === y.parent.right) y.parent.right = x;
        else y.parent.left = x;
        x.right = y;
        y.parent = x;
    }

    // --- Insert ---

    insert(key) {
        const z = new RBNode(key);
        z.left = this.NIL;
        z.right = this.NIL;
        z.parent = this.NIL;

        let y = this.NIL;
        let x = this.root;
        while (x !== this.NIL) {
            y = x;
            x = key < x.key ? x.left : x.right;
        }
        z.parent = y;
        if (y === this.NIL) this.root = z;
        else if (key < y.key) y.left = z;
        else y.right = z;

        this._size++;
        this._insertFixup(z);
        return z;
    }

    _insertFixup(z) {
        while (z.parent.color === RED) {
            if (z.parent === z.parent.parent.left) {
                const uncle = z.parent.parent.right;
                if (uncle.color === RED) {
                    z.parent.color = BLACK;
                    uncle.color = BLACK;
                    z.parent.parent.color = RED;
                    z = z.parent.parent;
                } else {
                    if (z === z.parent.right) {
                        z = z.parent;
                        this._leftRotate(z);
                    }
                    z.parent.color = BLACK;
                    z.parent.parent.color = RED;
                    this._rightRotate(z.parent.parent);
                }
            } else {
                const uncle = z.parent.parent.left;
                if (uncle.color === RED) {
                    z.parent.color = BLACK;
                    uncle.color = BLACK;
                    z.parent.parent.color = RED;
                    z = z.parent.parent;
                } else {
                    if (z === z.parent.left) {
                        z = z.parent;
                        this._rightRotate(z);
                    }
                    z.parent.color = BLACK;
                    z.parent.parent.color = RED;
                    this._leftRotate(z.parent.parent);
                }
            }
        }
        this.root.color = BLACK;
    }

    // --- Search ---

    search(key) {
        let n = this.root;
        while (n !== this.NIL) {
            if (key === n.key) return n;
            n = key < n.key ? n.left : n.right;
        }
        return this.NIL;
    }

    contains(key) { return this.search(key) !== this.NIL; }

    minimum(node) {
        while (node.left !== this.NIL) node = node.left;
        return node;
    }

    // --- Delete ---

    _transplant(u, v) {
        if (u.parent === this.NIL) this.root = v;
        else if (u === u.parent.left) u.parent.left = v;
        else u.parent.right = v;
        v.parent = u.parent;
    }

    delete(key) {
        const z = this.search(key);
        if (z === this.NIL) return false;

        let y = z;
        let yOrigColor = y.color;
        let x;

        if (z.left === this.NIL) {
            x = z.right;
            this._transplant(z, z.right);
        } else if (z.right === this.NIL) {
            x = z.left;
            this._transplant(z, z.left);
        } else {
            y = this.minimum(z.right);
            yOrigColor = y.color;
            x = y.right;
            if (y.parent === z) {
                x.parent = y;
            } else {
                this._transplant(y, y.right);
                y.right = z.right;
                y.right.parent = y;
            }
            this._transplant(z, y);
            y.left = z.left;
            y.left.parent = y;
            y.color = z.color;
        }

        this._size--;
        if (yOrigColor === BLACK) this._deleteFixup(x);
        return true;
    }

    _deleteFixup(x) {
        while (x !== this.root && x.color === BLACK) {
            if (x === x.parent.left) {
                let w = x.parent.right;
                if (w.color === RED) {
                    w.color = BLACK;
                    x.parent.color = RED;
                    this._leftRotate(x.parent);
                    w = x.parent.right;
                }
                if (w.left.color === BLACK && w.right.color === BLACK) {
                    w.color = RED;
                    x = x.parent;
                } else {
                    if (w.right.color === BLACK) {
                        w.left.color = BLACK;
                        w.color = RED;
                        this._rightRotate(w);
                        w = x.parent.right;
                    }
                    w.color = x.parent.color;
                    x.parent.color = BLACK;
                    w.right.color = BLACK;
                    this._leftRotate(x.parent);
                    x = this.root;
                }
            } else {
                let w = x.parent.left;
                if (w.color === RED) {
                    w.color = BLACK;
                    x.parent.color = RED;
                    this._rightRotate(x.parent);
                    w = x.parent.left;
                }
                if (w.right.color === BLACK && w.left.color === BLACK) {
                    w.color = RED;
                    x = x.parent;
                } else {
                    if (w.left.color === BLACK) {
                        w.right.color = BLACK;
                        w.color = RED;
                        this._leftRotate(w);
                        w = x.parent.left;
                    }
                    w.color = x.parent.color;
                    x.parent.color = BLACK;
                    w.left.color = BLACK;
                    this._rightRotate(x.parent);
                    x = this.root;
                }
            }
        }
        x.color = BLACK;
    }

    // --- Metrics ---

    height(node = this.root) {
        if (node === this.NIL) return -1;
        return 1 + Math.max(this.height(node.left), this.height(node.right));
    }

    blackHeight(node = this.root) {
        if (node === this.NIL) return 0;
        const lbh = this.blackHeight(node.left);
        return lbh + (node.left.color === BLACK ? 1 : 0);
    }

    // --- Traversals ---

    inorder(node = this.root, result = []) {
        if (node !== this.NIL) {
            this.inorder(node.left, result);
            result.push(node);
            this.inorder(node.right, result);
        }
        return result;
    }

    preorder(node = this.root, result = []) {
        if (node !== this.NIL) {
            result.push(node);
            this.preorder(node.left, result);
            this.preorder(node.right, result);
        }
        return result;
    }

    postorder(node = this.root, result = []) {
        if (node !== this.NIL) {
            this.postorder(node.left, result);
            this.postorder(node.right, result);
            result.push(node);
        }
        return result;
    }

    // --- Collect all nodes ---

    collectNodes(node = this.root, nodes = []) {
        if (node !== this.NIL) {
            nodes.push(node);
            this.collectNodes(node.left, nodes);
            this.collectNodes(node.right, nodes);
        }
        return nodes;
    }
}
