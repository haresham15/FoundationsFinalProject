"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { RBTree, RED, BLACK } from '@/lib/rbt';

const NODE_RADIUS = 22;
const LEVEL_HEIGHT = 70;
const MIN_H_SPACING = 50;

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
    textBlack: '#e6edf3'
};

export default function Home() {
    const [stats, setStats] = useState({ nodes: 0, height: 0, bh: 0 });
    const [logs, setLogs] = useState([]);
    const [traversalOutput, setTraversalOutput] = useState('');
    const [isTreeEmpty, setIsTreeEmpty] = useState(true);

    const [insertKey, setInsertKey] = useState('');
    const [deleteKey, setDeleteKey] = useState('');
    const [searchKey, setSearchKey] = useState('');

    const canvasRef = useRef(null);
    const containerRef = useRef(null);
    const treeRef = useRef(new RBTree());
    const panRef = useRef({ x: 0, y: 0 });
    const dragRef = useRef({ isDragging: false, startX: 0, startY: 0, lastX: 0, lastY: 0 });
    const animRef = useRef(null);

    const addLog = useCallback((message, type = 'info') => {
        const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setLogs(prev => {
            const newLogs = [{ time, msg: message, type }, ...prev];
            return newLogs.slice(0, 50);
        });
    }, []);

    const updateStats = useCallback(() => {
        const tree = treeRef.current;
        setIsTreeEmpty(tree.isEmpty);
        setStats({
            nodes: tree.size,
            height: tree.isEmpty ? 0 : tree.height(),
            bh: tree.isEmpty ? 0 : tree.blackHeight(),
        });
    }, []);

    const computeLayout = useCallback(() => {
        const tree = treeRef.current;
        if (tree.isEmpty) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const dpr = window.devicePixelRatio || 1;
        const canvasWidth = canvas.width / dpr;
        
        const nodes = tree.inorder();
        const hSpacing = Math.max(MIN_H_SPACING, canvasWidth / (nodes.length + 2));
        
        const inorderMap = new Map();
        nodes.forEach((n, i) => inorderMap.set(n, i));
        
        const startX = canvasWidth / 2 - (nodes.length * hSpacing) / 2 + hSpacing / 2;

        function setPositions(node, depth) {
            if (node === tree.NIL) return;
            setPositions(node.left, depth + 1);
            
            const idx = inorderMap.get(node);
            node.targetX = startX + idx * hSpacing;
            node.targetY = 60 + depth * LEVEL_HEIGHT;
            
            if (node.scale === 0) {
                node.x = node.targetX;
                node.y = node.targetY - 20;
            }
            node.targetScale = 1;
            
            setPositions(node.right, depth + 1);
        }
        setPositions(tree.root, 0);
    }, []);

    const renderTree = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const w = canvas.width / dpr;
        const h = canvas.height / dpr;
        
        ctx.clearRect(0, 0, w, h);
        const tree = treeRef.current;
        if (tree.isEmpty) return;

        ctx.save();
        ctx.translate(panRef.current.x, panRef.current.y);

        function drawEdge(parent, child) {
            const highlighted = parent.highlighted || child.highlighted;
            ctx.beginPath();
            ctx.moveTo(parent.x, parent.y + NODE_RADIUS * parent.scale);
            ctx.lineTo(child.x, child.y - NODE_RADIUS * child.scale);
            ctx.strokeStyle = highlighted ? COLORS.edgeHighlight : COLORS.edge;
            ctx.lineWidth = highlighted ? 2.5 : 1.5;
            ctx.stroke();
        }

        function drawEdges(node) {
            if (node === tree.NIL) return;
            if (node.left !== tree.NIL) { drawEdge(node, node.left); drawEdges(node.left); }
            if (node.right !== tree.NIL) { drawEdge(node, node.right); drawEdges(node.right); }
        }

        function drawNode(node) {
            if (node === tree.NIL) return;
            drawNode(node.left);
            drawNode(node.right);
            
            const r = NODE_RADIUS * node.scale;
            if (r < 1) return;
            
            const isRed = node.color === RED;
            const isHighlighted = node.highlighted;

            const glowColor = isHighlighted ? COLORS.highlightGlow : isRed ? COLORS.redGlow : COLORS.blackGlow;
            ctx.beginPath();
            ctx.arc(node.x, node.y, r + 6, 0, Math.PI * 2);
            ctx.fillStyle = glowColor;
            ctx.fill();

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

            ctx.fillStyle = COLORS.textWhite;
            ctx.font = `600 ${Math.round(13 * node.scale)}px 'Inter', sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(node.key.toString(), node.x, node.y);

            ctx.fillStyle = isHighlighted ? COLORS.highlightFill : isRed ? COLORS.redFill : COLORS.blackStroke;
            ctx.font = `500 ${Math.round(9 * node.scale)}px 'Inter', sans-serif`;
            ctx.fillText(isRed ? 'R' : 'B', node.x, node.y + r + 12);
        }

        drawEdges(tree.root);
        drawNode(tree.root);
        ctx.restore();
    }, []);

    const animate = useCallback(() => {
        const tree = treeRef.current;
        if (tree.isEmpty) {
            renderTree();
            return;
        }

        let needsUpdate = false;
        const allNodes = tree.collectNodes();

        for (const node of allNodes) {
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

            if (node.highlightTimer > 0) {
                node.highlightTimer -= 16;
                needsUpdate = true;
                if (node.highlightTimer <= 0) {
                    node.highlighted = false;
                    node.highlightTimer = 0;
                }
            }
        }

        renderTree();

        if (needsUpdate) {
            animRef.current = requestAnimationFrame(animate);
        } else {
            // Even if we stop mutating positions, the canvas might need to stay clean
            // It's already rendered, so we just let it sit.
        }
    }, [renderTree]);

    const startAnimation = useCallback(() => {
        if (animRef.current) cancelAnimationFrame(animRef.current);
        animRef.current = requestAnimationFrame(animate);
    }, [animate]);

    const resizeCanvas = useCallback(() => {
        if (!canvasRef.current || !containerRef.current) return;
        const dpr = window.devicePixelRatio || 1;
        const rect = containerRef.current.getBoundingClientRect();
        canvasRef.current.width = rect.width * dpr;
        canvasRef.current.height = rect.height * dpr;
        canvasRef.current.style.width = rect.width + 'px';
        canvasRef.current.style.height = rect.height + 'px';
        const ctx = canvasRef.current.getContext('2d');
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        computeLayout();
        renderTree();
    }, [computeLayout, renderTree]);

    // Initial event listeners
    useEffect(() => {
        addLog('Ready. Insert a node to begin.', 'info');
        window.addEventListener('resize', resizeCanvas);
        
        // Timeout to ensure the container is truly fully mounted
        const timer = setTimeout(resizeCanvas, 50);
        
        return () => {
            clearTimeout(timer);
            window.removeEventListener('resize', resizeCanvas);
            if (animRef.current) cancelAnimationFrame(animRef.current);
        };
    }, []); // Empty dependency array ensures it only runs on true mount

    const handleMouseDown = (e) => {
        dragRef.current.isDragging = true;
        dragRef.current.startX = e.clientX;
        dragRef.current.startY = e.clientY;
        dragRef.current.lastX = panRef.current.x;
        dragRef.current.lastY = panRef.current.y;
        e.target.style.cursor = 'grabbing';
    };

    const handleMouseMove = (e) => {
        if (!dragRef.current.isDragging) return;
        panRef.current.x = dragRef.current.lastX + (e.clientX - dragRef.current.startX);
        panRef.current.y = dragRef.current.lastY + (e.clientY - dragRef.current.startY);
        renderTree();
    };

    const handleMouseUpOrLeave = (e) => {
        dragRef.current.isDragging = false;
        e.target.style.cursor = 'grab';
    };

    const doInsert = (key) => {
        if (isNaN(key)) return addLog('Please enter a valid number.', 'warn');
        treeRef.current.insert(key);
        addLog(`Inserted ${key}`, 'insert');
        computeLayout();
        updateStats();
        startAnimation();
    };

    const doDelete = (key) => {
        if (isNaN(key)) return addLog('Please enter a valid number.', 'warn');
        if (treeRef.current.delete(key)) {
            addLog(`Deleted ${key}`, 'delete');
        } else {
            addLog(`Key ${key} not found.`, 'warn');
        }
        computeLayout();
        updateStats();
        startAnimation();
    };

    const doSearch = (key) => {
        if (isNaN(key)) return addLog('Please enter a valid number.', 'warn');
        const tree = treeRef.current;
        tree.collectNodes().forEach(n => { n.highlighted = false; n.highlightTimer = 0; });
        const node = tree.search(key);
        if (node !== tree.NIL) {
            node.highlighted = true;
            node.highlightTimer = 2000;
            addLog(`Found ${key}`, 'search');
            let current = tree.root;
            while (current !== tree.NIL && current !== node) {
                current.highlighted = true;
                current.highlightTimer = 1500;
                current = key < current.key ? current.left : current.right;
            }
        } else {
            addLog(`Key ${key} not found.`, 'warn');
        }
        startAnimation();
    };

    const handleRandomInsert = () => { doInsert(Math.floor(Math.random() * 999) + 1); };

    const handleRandomTree = () => {
        treeRef.current = new RBTree();
        panRef.current = { x: 0, y: 0 };
        const count = 10 + Math.floor(Math.random() * 11);
        const keys = new Set();
        while (keys.size < count) keys.add(Math.floor(Math.random() * 999) + 1);
        keys.forEach(k => treeRef.current.insert(k));
        addLog(`Generated random tree with ${count} nodes`, 'insert');
        computeLayout();
        updateStats();
        startAnimation();
    };

    const handleSampleTree = () => {
        treeRef.current = new RBTree();
        panRef.current = { x: 0, y: 0 };
        [41, 38, 31, 12, 19, 8, 50, 45, 60, 55, 70, 25].forEach(k => treeRef.current.insert(k));
        addLog('Loaded sample tree', 'info');
        computeLayout();
        updateStats();
        startAnimation();
    };

    const handleClear = () => {
        treeRef.current = new RBTree();
        panRef.current = { x: 0, y: 0 };
        addLog('Tree cleared.', 'info');
        computeLayout();
        updateStats();
        renderTree();
    };

    const handleTraversal = (type) => {
        const tree = treeRef.current;
        if (tree.isEmpty) return addLog('Tree is empty.', 'warn');
        let nodes;
        if (type === 'inorder') nodes = tree.inorder();
        if (type === 'preorder') nodes = tree.preorder();
        if (type === 'postorder') nodes = tree.postorder();
        
        const keys = nodes.map(n => n.key);
        setTraversalOutput(`${type}: [${keys.join(', ')}]`);
        addLog(`${type} traversal: ${keys.length} nodes`, 'search');
        
        nodes.forEach((n, i) => {
            setTimeout(() => {
                n.highlighted = true;
                n.highlightTimer = 800;
                startAnimation();
            }, i * 100);
        });
    };

    return (
        <div className="app">
            <header className="header" id="header">
                <div className="header-content">
                    <div className="logo">
                        <div className="logo-icon">
                            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                                <circle cx="14" cy="6" r="5" fill="#f85149" stroke="#30363d" strokeWidth="1.5"/>
                                <circle cx="7" cy="20" r="5" fill="#1a1a2e" stroke="#f85149" strokeWidth="1.5"/>
                                <circle cx="21" cy="20" r="5" fill="#1a1a2e" stroke="#f85149" strokeWidth="1.5"/>
                                <line x1="14" y1="11" x2="7" y2="15" stroke="#484f58" strokeWidth="1.5"/>
                                <line x1="14" y1="11" x2="21" y2="15" stroke="#484f58" strokeWidth="1.5"/>
                            </svg>
                        </div>
                        <h1>Red-Black Tree <span className="accent">Visualizer</span></h1>
                    </div>
                    <div className="stats-bar">
                        <div className="stat"><span className="stat-label">Nodes</span><span className="stat-value">{stats.nodes}</span></div>
                        <div className="stat"><span className="stat-label">Height</span><span className="stat-value">{stats.height}</span></div>
                        <div className="stat"><span className="stat-label">Black-Height</span><span className="stat-value">{stats.bh}</span></div>
                    </div>
                </div>
            </header>

            <main className="main">
                <aside className="controls-panel">
                    <div className="control-group">
                        <label className="control-label">Insert Node</label>
                        <div className="input-row">
                            <input type="number" className="input-field" placeholder="Key value" 
                                value={insertKey} onChange={e => setInsertKey(e.target.value)}
                                onKeyDown={e => { if (e.key === 'Enter') { doInsert(parseInt(insertKey)); setInsertKey(''); }}} />
                            <button className="btn btn-primary" onClick={() => { doInsert(parseInt(insertKey)); setInsertKey(''); }}>
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/></svg>
                                Insert
                            </button>
                        </div>
                    </div>

                    <div className="control-group">
                        <label className="control-label">Delete Node</label>
                        <div className="input-row">
                            <input type="number" className="input-field" placeholder="Key value" 
                                value={deleteKey} onChange={e => setDeleteKey(e.target.value)}
                                onKeyDown={e => { if (e.key === 'Enter') { doDelete(parseInt(deleteKey)); setDeleteKey(''); }}} />
                            <button className="btn btn-danger" onClick={() => { doDelete(parseInt(deleteKey)); setDeleteKey(''); }}>
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/></svg>
                                Delete
                            </button>
                        </div>
                    </div>

                    <div className="control-group">
                        <label className="control-label">Search Node</label>
                        <div className="input-row">
                            <input type="number" className="input-field" placeholder="Key value" 
                                value={searchKey} onChange={e => setSearchKey(e.target.value)}
                                onKeyDown={e => { if (e.key === 'Enter') { doSearch(parseInt(searchKey)); setSearchKey(''); }}} />
                            <button className="btn btn-search" onClick={() => { doSearch(parseInt(searchKey)); setSearchKey(''); }}>
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M11.5 7a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zm-.82 4.74a6 6 0 111.06-1.06l3.04 3.04a.75.75 0 11-1.06 1.06l-3.04-3.04z"/></svg>
                                Search
                            </button>
                        </div>
                    </div>

                    <div className="divider"></div>

                    <div className="control-group">
                        <label className="control-label">Quick Actions</label>
                        <div className="btn-grid">
                            <button className="btn btn-secondary" onClick={handleRandomInsert}>Random Insert</button>
                            <button className="btn btn-secondary" onClick={handleRandomTree}>Random Tree</button>
                            <button className="btn btn-secondary" onClick={handleSampleTree}>Sample Tree</button>
                            <button className="btn btn-ghost" onClick={handleClear}>Clear Tree</button>
                        </div>
                    </div>

                    <div className="divider"></div>

                    <div className="control-group">
                        <label className="control-label">Traversal</label>
                        <div className="btn-grid">
                            <button className="btn btn-secondary btn-sm" onClick={() => handleTraversal('inorder')}>In-Order</button>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleTraversal('preorder')}>Pre-Order</button>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleTraversal('postorder')}>Post-Order</button>
                        </div>
                        <div className={`traversal-output ${traversalOutput ? 'show' : ''}`}>{traversalOutput}</div>
                    </div>

                    <div className="divider"></div>

                    <div className="control-group">
                        <label className="control-label">Operation Log</label>
                        <div className="log-container">
                            {logs.map((log, i) => (
                                <div key={i} className={`log-entry log-${log.type}`}>[{log.time}] {log.msg}</div>
                            ))}
                        </div>
                    </div>
                </aside>

                <div className="canvas-container" ref={containerRef}>
                    <canvas id="tree-canvas" ref={canvasRef} style={{cursor: 'grab'}}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUpOrLeave}
                        onMouseLeave={handleMouseUpOrLeave}></canvas>
                    {isTreeEmpty && (
                        <div className="empty-state">
                            <div className="empty-icon">
                                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                                    <circle cx="32" cy="16" r="10" fill="#21262d" stroke="#30363d" strokeWidth="2"/>
                                    <circle cx="16" cy="44" r="8" fill="#21262d" stroke="#30363d" strokeWidth="2"/>
                                    <circle cx="48" cy="44" r="8" fill="#21262d" stroke="#30363d" strokeWidth="2"/>
                                    <line x1="32" y1="26" x2="16" y2="36" stroke="#30363d" strokeWidth="2"/>
                                    <line x1="32" y1="26" x2="48" y2="36" stroke="#30363d" strokeWidth="2"/>
                                </svg>
                            </div>
                            <p className="empty-text">Insert a node to visualize the tree</p>
                            <p className="empty-hint">Or click <strong>Sample Tree</strong> to see an example</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
