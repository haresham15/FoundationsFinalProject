/**
 * Red-Black Tree Visualizer
 * ==========================
 * Interactive canvas-based visualization of a Red-Black Tree.
 * Implements full RBT logic in JavaScript for real-time rendering.
 */

// ====================================================================
// Constants
// ====================================================================

const RED = 0;
const BLACK = 1;

const NODE_RADIUS = 22;
const LEVEL_HEIGHT = 70;
const MIN_H_SPACING = 50;
const ANIMATION_DURATION = 400;

const COLORS = {
    redFill: '#f85149',
    redStroke: '#da3633',
    redGlow: 'rgba(248, 81, 73, 0.35)',
    blackFill: '#1c2028',
    blackStroke: '#484f58',
    blackGlow: 'rgba(72, 79, 88, 0.2)',
    highlightFill: '#58a6ff',
    highlightStroke: '#1f6feb',
    highlightGlow: 'rgba(88, 166, 255, 0.4)',
    edge: '#30363d',
    edgeHighlight: '#58a6ff',
    textWhite: '#e6edf3',
    textBlack: '#e6edf3',
    nilFill: '#21262d',
    nilStroke: '#30363d',
};

// ====================================================================
// Red-Black Tree Data Structure
// ====================================================================

class RBNode {
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

class RBTree {
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

// ====================================================================
// Visualization Engine
// ====================================================================

const canvas = document.getElementById('tree-canvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('canvas-container');
const emptyState = document.getElementById('empty-state');

let tree = new RBTree();
let animationFrame = null;
let panX = 0, panY = 0;
let isDragging = false;
let dragStartX = 0, dragStartY = 0;
let lastPanX = 0, lastPanY = 0;

// --- Resize ---

function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
}

window.addEventListener('resize', resizeCanvas);

// --- Pan support ---

canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    lastPanX = panX;
    lastPanY = panY;
    canvas.style.cursor = 'grabbing';
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    panX = lastPanX + (e.clientX - dragStartX);
    panY = lastPanY + (e.clientY - dragStartY);
    render();
});

canvas.addEventListener('mouseup', () => {
    isDragging = false;
    canvas.style.cursor = 'grab';
});

canvas.addEventListener('mouseleave', () => {
    isDragging = false;
    canvas.style.cursor = 'default';
});

// --- Layout calculation ---

function computeLayout() {
    if (tree.isEmpty) return;

    // Compute positions using an in-order index for x-spacing
    const nodes = tree.inorder();
    const totalHeight = tree.height();
    const canvasWidth = canvas.width / (window.devicePixelRatio || 1);
    const canvasHeight = canvas.height / (window.devicePixelRatio || 1);

    // Calculate horizontal spacing
    const hSpacing = Math.max(MIN_H_SPACING, canvasWidth / (nodes.length + 2));

    // Assign x based on in-order index, y based on depth
    const inorderMap = new Map();
    nodes.forEach((n, i) => {
        inorderMap.set(n, i);
    });

    const startX = canvasWidth / 2 - (nodes.length * hSpacing) / 2 + hSpacing / 2;

    function setPositions(node, depth) {
        if (node === tree.NIL) return;
        setPositions(node.left, depth + 1);

        const idx = inorderMap.get(node);
        node.targetX = startX + idx * hSpacing;
        node.targetY = 60 + depth * LEVEL_HEIGHT;

        // Initialize position for new nodes
        if (node.scale === 0) {
            node.x = node.targetX;
            node.y = node.targetY - 20;
        }

        node.targetScale = 1;
        setPositions(node.right, depth + 1);
    }

    setPositions(tree.root, 0);
}

// --- Animation loop ---

function animate() {
    if (tree.isEmpty) {
        render();
        return;
    }

    let needsUpdate = false;
    const allNodes = tree.collectNodes();

    for (const node of allNodes) {
        // Smooth position interpolation
        const dx = node.targetX - node.x;
        const dy = node.targetY - node.y;
        const ds = node.targetScale - node.scale;

        if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5 || Math.abs(ds) > 0.01) {
            node.x += dx * 0.15;
            node.y += dy * 0.15;
            node.scale += ds * 0.15;
            needsUpdate = true;
        } else {
            node.x = node.targetX;
            node.y = node.targetY;
            node.scale = node.targetScale;
        }

        // Highlight fade
        if (node.highlightTimer > 0) {
            node.highlightTimer -= 16;
            needsUpdate = true;
            if (node.highlightTimer <= 0) {
                node.highlighted = false;
                node.highlightTimer = 0;
            }
        }
    }

    render();

    if (needsUpdate) {
        animationFrame = requestAnimationFrame(animate);
    }
}

function startAnimation() {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(animate);
}

// --- Rendering ---

function render() {
    const w = canvas.width / (window.devicePixelRatio || 1);
    const h = canvas.height / (window.devicePixelRatio || 1);
    ctx.clearRect(0, 0, w, h);

    if (tree.isEmpty) {
        emptyState.classList.remove('hidden');
        return;
    }
    emptyState.classList.add('hidden');

    ctx.save();
    ctx.translate(panX, panY);

    // Draw edges first
    drawEdges(tree.root);
    // Draw nodes on top
    drawNodes(tree.root);

    ctx.restore();
}

function drawEdges(node) {
    if (node === tree.NIL) return;

    if (node.left !== tree.NIL) {
        drawEdge(node, node.left);
        drawEdges(node.left);
    }
    if (node.right !== tree.NIL) {
        drawEdge(node, node.right);
        drawEdges(node.right);
    }
}

function drawEdge(parent, child) {
    const highlighted = parent.highlighted || child.highlighted;

    ctx.beginPath();
    ctx.moveTo(parent.x, parent.y + NODE_RADIUS * parent.scale);
    ctx.lineTo(child.x, child.y - NODE_RADIUS * child.scale);
    ctx.strokeStyle = highlighted ? COLORS.edgeHighlight : COLORS.edge;
    ctx.lineWidth = highlighted ? 2.5 : 1.5;
    ctx.stroke();
}

function drawNodes(node) {
    if (node === tree.NIL) return;

    drawNodes(node.left);
    drawNodes(node.right);
    drawNode(node);
}

function drawNode(node) {
    const r = NODE_RADIUS * node.scale;
    if (r < 1) return;

    const isRed = node.color === RED;
    const isHighlighted = node.highlighted;

    // Glow effect
    const glowColor = isHighlighted ? COLORS.highlightGlow :
                      isRed ? COLORS.redGlow : COLORS.blackGlow;
    ctx.beginPath();
    ctx.arc(node.x, node.y, r + 6, 0, Math.PI * 2);
    ctx.fillStyle = glowColor;
    ctx.fill();

    // Node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2);

    if (isHighlighted) {
        ctx.fillStyle = COLORS.highlightFill;
        ctx.strokeStyle = COLORS.highlightStroke;
    } else if (isRed) {
        ctx.fillStyle = COLORS.redFill;
        ctx.strokeStyle = COLORS.redStroke;
    } else {
        ctx.fillStyle = COLORS.blackFill;
        ctx.strokeStyle = COLORS.blackStroke;
    }

    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    // Key text
    ctx.fillStyle = COLORS.textWhite;
    ctx.font = `600 ${Math.round(13 * node.scale)}px 'Inter', sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(node.key.toString(), node.x, node.y);

    // Color label below
    ctx.fillStyle = isHighlighted ? COLORS.highlightFill :
                    isRed ? COLORS.redFill : COLORS.blackStroke;
    ctx.font = `500 ${Math.round(9 * node.scale)}px 'Inter', sans-serif`;
    ctx.fillText(isRed ? 'R' : 'B', node.x, node.y + r + 12);
}

// ====================================================================
// Event Handlers
// ====================================================================

function handleInsert() {
    const input = document.getElementById('insert-input');
    const key = parseInt(input.value);
    if (isNaN(key)) {
        addLog('Please enter a valid number.', 'warn');
        return;
    }
    tree.insert(key);
    addLog(`Inserted ${key}`, 'insert');
    input.value = '';
    input.focus();
    computeLayout();
    updateStats();
    startAnimation();
}

function handleDelete() {
    const input = document.getElementById('delete-input');
    const key = parseInt(input.value);
    if (isNaN(key)) {
        addLog('Please enter a valid number.', 'warn');
        return;
    }
    if (tree.delete(key)) {
        addLog(`Deleted ${key}`, 'delete');
    } else {
        addLog(`Key ${key} not found.`, 'warn');
    }
    input.value = '';
    input.focus();
    computeLayout();
    updateStats();
    startAnimation();
}

function handleSearch() {
    const input = document.getElementById('search-input');
    const key = parseInt(input.value);
    if (isNaN(key)) {
        addLog('Please enter a valid number.', 'warn');
        return;
    }

    // Clear previous highlights
    tree.collectNodes().forEach(n => {
        n.highlighted = false;
        n.highlightTimer = 0;
    });

    const node = tree.search(key);
    if (node !== tree.NIL) {
        node.highlighted = true;
        node.highlightTimer = 2000;
        addLog(`Found ${key}`, 'search');

        // Also highlight the search path
        let current = tree.root;
        while (current !== tree.NIL && current !== node) {
            current.highlighted = true;
            current.highlightTimer = 1500;
            current = key < current.key ? current.left : current.right;
        }
    } else {
        addLog(`Key ${key} not found.`, 'warn');
    }
    input.value = '';
    input.focus();
    startAnimation();
}

function handleRandomInsert() {
    const key = Math.floor(Math.random() * 999) + 1;
    tree.insert(key);
    addLog(`Inserted ${key} (random)`, 'insert');
    computeLayout();
    updateStats();
    startAnimation();
}

function handleRandomTree() {
    tree = new RBTree();
    panX = 0;
    panY = 0;
    const count = 10 + Math.floor(Math.random() * 11);
    const keys = new Set();
    while (keys.size < count) keys.add(Math.floor(Math.random() * 999) + 1);
    keys.forEach(k => tree.insert(k));
    addLog(`Generated random tree with ${count} nodes`, 'insert');
    computeLayout();
    updateStats();
    startAnimation();
}

function handleSampleTree() {
    tree = new RBTree();
    panX = 0;
    panY = 0;
    [41, 38, 31, 12, 19, 8, 50, 45, 60, 55, 70, 25].forEach(k => tree.insert(k));
    addLog('Loaded sample tree: [41, 38, 31, 12, 19, 8, 50, 45, 60, 55, 70, 25]', 'info');
    computeLayout();
    updateStats();
    startAnimation();
}

function handleClear() {
    tree = new RBTree();
    panX = 0;
    panY = 0;
    addLog('Tree cleared.', 'info');
    computeLayout();
    updateStats();
    render();
}

function handleTraversal(type) {
    if (tree.isEmpty) {
        addLog('Tree is empty.', 'warn');
        return;
    }

    let nodes;
    switch (type) {
        case 'inorder': nodes = tree.inorder(); break;
        case 'preorder': nodes = tree.preorder(); break;
        case 'postorder': nodes = tree.postorder(); break;
    }

    const keys = nodes.map(n => n.key);
    const output = document.getElementById('traversal-output');
    output.textContent = `${type}: [${keys.join(', ')}]`;
    output.classList.add('show');
    addLog(`${type} traversal: ${keys.length} nodes`, 'search');

    // Animate traversal path
    nodes.forEach((n, i) => {
        setTimeout(() => {
            n.highlighted = true;
            n.highlightTimer = 800;
            startAnimation();
        }, i * 100);
    });
}

// ====================================================================
// UI Helpers
// ====================================================================

function updateStats() {
    document.getElementById('stat-nodes').textContent = tree.size;
    document.getElementById('stat-height').textContent = 
        tree.isEmpty ? '0' : tree.height();
    document.getElementById('stat-bh').textContent = 
        tree.isEmpty ? '0' : tree.blackHeight();
}

function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    const time = new Date().toLocaleTimeString('en-US', { 
        hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' 
    });
    entry.textContent = `[${time}] ${message}`;

    logContainer.insertBefore(entry, logContainer.firstChild);

    // Keep max 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

// --- Keyboard shortcuts ---

document.getElementById('insert-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleInsert();
});

document.getElementById('delete-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleDelete();
});

document.getElementById('search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSearch();
});

// ====================================================================
// Initialization
// ====================================================================

resizeCanvas();
canvas.style.cursor = 'grab';
updateStats();
