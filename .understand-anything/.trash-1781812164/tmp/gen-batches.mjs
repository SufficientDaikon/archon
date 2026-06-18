import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';

const batchGroupPath = 'C:/Users/tahaa/Archon/.understand-anything/tmp/batch-group-1.json';
const intermediateDir = 'C:/Users/tahaa/Archon/.understand-anything/intermediate';

if (!existsSync(intermediateDir)) {
  mkdirSync(intermediateDir, { recursive: true });
}

const batchGroup = JSON.parse(readFileSync(batchGroupPath, 'utf8'));

function getNodeType(file) {
  const { fileCategory, path: fp } = file;
  if (fileCategory === 'docs') return 'document';
  if (fileCategory === 'infra') return 'pipeline';
  if (fileCategory === 'config') return 'config';
  if (fileCategory === 'code') return 'file';
  return 'file';
}

function isSignificantFunction(fn, exports) {
  const lineCount = (fn.endLine - fn.startLine + 1);
  const isExported = exports && exports.some(e => e.name === fn.name);
  return lineCount >= 10 || isExported;
}

function isSignificantClass(cls, exports) {
  const lineCount = (cls.endLine - cls.startLine + 1);
  const isExported = exports && exports.some(e => e.name === cls.name);
  return (cls.methods && cls.methods.length >= 2) || lineCount >= 20 || isExported;
}

for (const batch of batchGroup.batches) {
  const { batchIndex, files, batchImportData } = batch;

  const extractPath = `C:/Users/tahaa/Archon/.understand-anything/tmp/ua-file-extract-results-${batchIndex}.json`;
  const extract = JSON.parse(readFileSync(extractPath, 'utf8'));

  const extractByPath = {};
  for (const r of (extract.results || [])) {
    extractByPath[r.path] = r;
  }

  const nodes = [];
  const edges = [];
  const seenEdges = new Set();

  function addEdge(edge) {
    const key = `${edge.type}:${edge.source}:${edge.target}`;
    if (!seenEdges.has(key)) {
      seenEdges.add(key);
      edges.push(edge);
    }
  }

  let expectedImportEdgeCount = 0;
  for (const imports of Object.values(batchImportData)) {
    expectedImportEdgeCount += imports.length;
  }

  for (const file of files) {
    const fp = file.path;
    const nodeType = getNodeType(file);
    const extractResult = extractByPath[fp];

    const fileNodeId = `${nodeType}:${fp}`;
    const fileNode = {
      id: fileNodeId,
      type: nodeType,
      path: fp,
      label: fp.split('/').pop(),
      language: file.language,
      sizeLines: file.sizeLines,
      metadata: {
        fileCategory: file.fileCategory,
      }
    };

    if (extractResult) {
      fileNode.metadata.totalLines = extractResult.totalLines || file.sizeLines;
      fileNode.metadata.nonEmptyLines = extractResult.nonEmptyLines || 0;
      if (extractResult.metrics) {
        fileNode.metadata.metrics = extractResult.metrics;
      }
    }

    nodes.push(fileNode);

    if (extractResult && file.fileCategory === 'code') {
      const exports = extractResult.exports || [];

      for (const fn of (extractResult.functions || [])) {
        if (isSignificantFunction(fn, exports)) {
          const fnNodeId = `function:${fp}:${fn.name}`;
          const isExported = exports.some(e => e.name === fn.name);
          nodes.push({
            id: fnNodeId,
            type: 'function',
            path: fp,
            label: fn.name,
            language: file.language,
            metadata: {
              startLine: fn.startLine,
              endLine: fn.endLine,
              lineCount: fn.endLine - fn.startLine + 1,
              params: fn.params || [],
              exported: isExported,
            }
          });
          addEdge({ type: 'contains', source: fileNodeId, target: fnNodeId, weight: 1.0 });
        }
      }

      for (const cls of (extractResult.classes || [])) {
        if (isSignificantClass(cls, exports)) {
          const clsNodeId = `class:${fp}:${cls.name}`;
          const isExported = exports.some(e => e.name === cls.name);
          nodes.push({
            id: clsNodeId,
            type: 'class',
            path: fp,
            label: cls.name,
            language: file.language,
            metadata: {
              startLine: cls.startLine,
              endLine: cls.endLine,
              lineCount: cls.endLine - cls.startLine + 1,
              methods: cls.methods || [],
              exported: isExported,
            }
          });
          addEdge({ type: 'contains', source: fileNodeId, target: clsNodeId, weight: 1.0 });
        }
      }
    }

    const imports = batchImportData[fp] || [];
    for (const importedPath of imports) {
      const importedFile = files.find(f => f.path === importedPath);
      let importedType;
      if (importedFile) {
        importedType = getNodeType(importedFile);
      } else {
        importedType = 'file';
      }
      const targetId = `${importedType}:${importedPath}`;
      addEdge({ type: 'imports', source: fileNodeId, target: targetId, weight: 0.7 });
    }
  }

  const actualImportEdgeCount = edges.filter(e => e.type === 'imports').length;

  if (actualImportEdgeCount !== expectedImportEdgeCount) {
    console.error(`BATCH ${batchIndex}: import edge mismatch! Expected ${expectedImportEdgeCount}, got ${actualImportEdgeCount}`);
  } else {
    console.log(`Batch ${batchIndex}: ${nodes.length} nodes, ${edges.length} edges, ${actualImportEdgeCount} import edges (verified OK)`);
  }

  const MAX_NODES = 60;
  const MAX_EDGES = 120;

  if (nodes.length > MAX_NODES || edges.length > MAX_EDGES) {
    console.log(`  -> Splitting batch ${batchIndex} (${nodes.length} nodes, ${edges.length} edges)...`);

    const parts = [];
    let i = 0;
    while (i < nodes.length) {
      const chunkNodes = nodes.slice(i, i + MAX_NODES);
      const chunkNodeIds = new Set(chunkNodes.map(n => n.id));
      const chunkEdges = edges.filter(e => chunkNodeIds.has(e.source) && chunkNodeIds.has(e.target));
      parts.push({ nodes: chunkNodes, edges: chunkEdges });
      i += MAX_NODES;
    }

    for (let p = 0; p < parts.length; p++) {
      const outPath = `${intermediateDir}/batch-${batchIndex}-part-${p + 1}.json`;
      const output = {
        batchIndex,
        part: p + 1,
        totalParts: parts.length,
        nodes: parts[p].nodes,
        edges: parts[p].edges,
      };
      writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');
      console.log(`  -> Wrote batch-${batchIndex}-part-${p + 1}.json (${parts[p].nodes.length} nodes, ${parts[p].edges.length} edges)`);
    }
  } else {
    const outPath = `${intermediateDir}/batch-${batchIndex}.json`;
    const output = {
      batchIndex,
      nodes,
      edges,
    };
    writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');
    console.log(`  -> Wrote batch-${batchIndex}.json`);
  }
}

console.log('\nAll 13 batches complete.');
