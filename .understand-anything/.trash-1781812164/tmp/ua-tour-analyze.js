#!/usr/bin/env node
// ua-tour-analyze.js — Graph topology analysis for Archon tour design

const fs = require('fs');

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  process.stderr.write('Usage: node ua-tour-analyze.js <input.json> <output.json>\n');
  process.exit(1);
}

let data;
try {
  data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
} catch (e) {
  process.stderr.write('Failed to parse input: ' + e.message + '\n');
  process.exit(1);
}

const { nodes = [], edges = [], layers = [] } = data;

// Build adjacency structures
const fanIn = {};
const fanOut = {};
nodes.forEach(n => { fanIn[n.id] = 0; fanOut[n.id] = 0; });

edges.forEach(e => {
  if (fanIn[e.target] !== undefined) fanIn[e.target]++;
  if (fanOut[e.source] !== undefined) fanOut[e.source]++;
});

// A. Fan-In Ranking
const fanInRanking = nodes
  .map(n => ({ id: n.id, fanIn: fanIn[n.id] || 0, name: n.name || n.label || n.id }))
  .sort((a, b) => b.fanIn - a.fanIn)
  .slice(0, 20);

// B. Fan-Out Ranking
const fanOutRanking = nodes
  .map(n => ({ id: n.id, fanOut: fanOut[n.id] || 0, name: n.name || n.label || n.id }))
  .sort((a, b) => b.fanOut - a.fanOut)
  .slice(0, 20);

// C. Entry Point Candidates
const codeEntryNames = [
  'index.ts','index.js','main.ts','main.js','app.ts','app.js',
  'server.ts','server.js','mod.rs','main.go','main.py','main.rs',
  'manage.py','app.py','wsgi.py','asgi.py','run.py','__main__.py',
  'Application.java','Main.java','Program.cs','config.ru','index.php',
  'cli.py'
];

const totalNodes = nodes.length;
const fanOutValues = nodes.map(n => fanOut[n.id] || 0).sort((a,b)=>a-b);
const fanInValues = nodes.map(n => fanIn[n.id] || 0).sort((a,b)=>a-b);
const fanOutTop10Threshold = fanOutValues[Math.floor(totalNodes * 0.9)] || 0;
const fanInBottom25Threshold = fanInValues[Math.floor(totalNodes * 0.25)] || 0;

const entryScores = nodes.map(n => {
  let score = 0;
  const path = n.path || n.filePath || '';
  const name = n.name || n.label || '';

  if (n.type === 'document') {
    if (name === 'README.md' && (path === 'README.md' || path === '')) score += 5;
    else if (name.endsWith('.md') && !path.includes('/')) score += 2;
  } else {
    if (codeEntryNames.some(en => name === en)) score += 3;
    const depth = path.split('/').length;
    if (depth <= 2) score += 1;
    if ((fanOut[n.id] || 0) >= fanOutTop10Threshold) score += 1;
    if ((fanIn[n.id] || 0) <= fanInBottom25Threshold) score += 1;
  }

  return { id: n.id, score, name, summary: n.summary || '' };
}).filter(e => e.score > 0).sort((a, b) => b.score - a.score).slice(0, 5);

// D. BFS Traversal from top code entry point
const topCodeEntry = entryScores.find(e => {
  const n = nodes.find(x => x.id === e.id);
  return n && n.type !== 'document';
});

let bfsTraversal = { startNode: null, order: [], depthMap: {}, byDepth: {} };
if (topCodeEntry) {
  const start = topCodeEntry.id;
  const visited = new Set();
  const queue = [{ id: start, depth: 0 }];
  visited.add(start);
  const importEdgeTypes = new Set(['imports', 'calls']);

  while (queue.length > 0) {
    const { id, depth } = queue.shift();
    bfsTraversal.order.push(id);
    bfsTraversal.depthMap[id] = depth;
    if (!bfsTraversal.byDepth[depth]) bfsTraversal.byDepth[depth] = [];
    bfsTraversal.byDepth[depth].push(id);

    const neighbors = edges
      .filter(e => e.source === id && importEdgeTypes.has(e.type))
      .map(e => e.target);

    for (const nb of neighbors) {
      if (!visited.has(nb)) {
        visited.add(nb);
        queue.push({ id: nb, depth: depth + 1 });
      }
    }
  }
  bfsTraversal.startNode = start;
}

// E. Non-Code File Inventory
const docTypes = new Set(['document']);
const infraTypes = new Set(['service', 'pipeline', 'resource']);
const dataTypes = new Set(['table', 'schema', 'endpoint']);
const configTypes = new Set(['config']);

const nonCodeFiles = {
  documentation: nodes.filter(n => docTypes.has(n.type)).map(n => ({
    id: n.id, name: n.name || n.label || n.id, summary: n.summary || ''
  })),
  infrastructure: nodes.filter(n => infraTypes.has(n.type)).map(n => ({
    id: n.id, name: n.name || n.label || n.id, type: n.type, summary: n.summary || ''
  })),
  data: nodes.filter(n => dataTypes.has(n.type)).map(n => ({
    id: n.id, name: n.name || n.label || n.id, summary: n.summary || ''
  })),
  config: nodes.filter(n => configTypes.has(n.type)).map(n => ({
    id: n.id, name: n.name || n.label || n.id, summary: n.summary || ''
  }))
};

// F. Tightly Coupled Clusters
const bidir = new Map();
edges.forEach(e => {
  const key = [e.source, e.target].sort().join('||');
  if (!bidir.has(key)) bidir.set(key, { a: e.source, b: e.target, count: 0 });
  bidir.get(key).count++;
});

const clusters = [];
const clusterSeed = [...bidir.values()].filter(p => p.count >= 2);
clusterSeed.forEach(pair => {
  clusters.push({ nodes: [pair.a, pair.b], edgeCount: pair.count });
});
// Expand clusters
clusters.sort((a, b) => b.edgeCount - a.edgeCount);

// G. Layer List
const layerResult = {
  count: layers.length,
  list: layers.map(l => ({ id: l.id, name: l.name, description: l.description || '' }))
};

// H. Node Summary Index
const nodeSummaryIndex = {};
nodes.forEach(n => {
  nodeSummaryIndex[n.id] = {
    name: n.name || n.label || n.id,
    type: n.type,
    summary: n.summary || n.description || ''
  };
});

const result = {
  scriptCompleted: true,
  entryPointCandidates: entryScores,
  fanInRanking,
  fanOutRanking,
  bfsTraversal,
  nonCodeFiles,
  clusters: clusters.slice(0, 10),
  layers: layerResult,
  nodeSummaryIndex,
  totalNodes: nodes.length,
  totalEdges: edges.length
};

try {
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.log('Analysis complete. Written to:', outputPath);
} catch (e) {
  process.stderr.write('Failed to write output: ' + e.message + '\n');
  process.exit(1);
}
process.exit(0);
