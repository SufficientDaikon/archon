const fs = require('fs');
const data = JSON.parse(fs.readFileSync('C:/Users/tahaa/Archon/.understand-anything/intermediate/assembled-graph.json', 'utf8'));
const nodes = data.nodes || [];

console.log('Total nodes to assign:', nodes.length);

const layers = [
  {
    id: "layer-infrastructure",
    label: "Infrastructure & CI/CD",
    description: "GitHub Actions workflows for CI, PyPI publishing, and GitHub Pages deployment — the build and release backbone for the Archon framework.",
    color: "#6b7280",
    order: 0
  },
  {
    id: "layer-config",
    label: "Configuration & Schemas",
    description: "Project manifest (archon.yaml), pyproject.toml, JSON/YAML schemas for all manifest types, and per-component config files that define the structure of skills, agents, bundles, pipelines, and synapses.",
    color: "#8b5cf6",
    order: 1
  },
  {
    id: "layer-component-library",
    label: "Skill & Agent Component Library",
    description: "The 99 skill directories, 14 agent definitions, 16 bundles, 5 synapses, and 9 pipelines — the declarative YAML manifests and supporting resource files that make up Archon's installable cognitive components.",
    color: "#0ea5e9",
    order: 2
  },
  {
    id: "layer-core-engine",
    label: "Core Engine",
    description: "The Python package (src/archon/) containing the CLI, registry, pipeline engine, synapse engine, policy engine, MCP schema generator, installer, and all supporting commands — the runtime brain of the Archon framework.",
    color: "#f59e0b",
    order: 3
  },
  {
    id: "layer-runtime-hooks",
    label: "Runtime Hook Layer",
    description: "Claude Code hook scripts (hooks/claude/) that fire at session start, prompt submission, pre/post tool use, and stop events to inject context, enforce guards, and track quality signals in real time.",
    color: "#ef4444",
    order: 4
  },
  {
    id: "layer-sdk-servers",
    label: "SDK & MCP Servers",
    description: "The public Python SDK (sdk/archon.py), the Rust file-ops server, the Forge MCP server, agent-router and skill-router servers — the programmatic interfaces and language-bridge components for integrating Archon into external systems.",
    color: "#10b981",
    order: 5
  },
  {
    id: "layer-tooling",
    label: "Developer Tooling & Scripts",
    description: "The VS Code extension, utility scripts (build_docs, generate-agent-cards, skill-compliance-check, etc.), test suites, and the .claude session-state XML files — tools that support development, validation, and debugging of Archon itself.",
    color: "#f97316",
    order: 6
  },
  {
    id: "layer-ui",
    label: "Web Dashboard",
    description: "The Next.js webapp (webapp/src/) providing an interactive browser-based dashboard for browsing and exploring installed Archon skills, agents, bundles, synapses, and pipelines.",
    color: "#ec4899",
    order: 7
  }
];

const nodeLayerMap = {};

function assign(id, layerId) {
  nodeLayerMap[id] = layerId;
}

for (const node of nodes) {
  const id = node.id;
  const path = node.path || id.replace(/^[^:]+:/, '');
  const type = node.type;

  if (type === 'pipeline') {
    assign(id, 'layer-infrastructure');
    continue;
  }

  if (type === 'document') {
    const p = id.replace('document:', '');
    if (p.startsWith('skills/') || p.startsWith('agents/') || p.startsWith('bundles/') || p.startsWith('synapses/') || p.startsWith('pipelines/')) {
      assign(id, 'layer-component-library');
    } else {
      assign(id, 'layer-tooling');
    }
    continue;
  }

  if (type === 'config') {
    const p = id.replace('config:', '');
    if (p.startsWith('.github/') || p.startsWith('.claude/')) {
      assign(id, 'layer-infrastructure');
    } else if (p.startsWith('skills/') || p.startsWith('agents/') || p.startsWith('bundles/') || p.startsWith('synapses/') || p.startsWith('pipelines/')) {
      assign(id, 'layer-component-library');
    } else if (p.startsWith('schemas/') || p === 'archon.yaml' || p === 'pyproject.toml' || p === 'catalog/catalog.yaml') {
      assign(id, 'layer-config');
    } else if (p.startsWith('webapp/')) {
      assign(id, 'layer-ui');
    } else if (p.startsWith('vscode-extension/')) {
      assign(id, 'layer-tooling');
    } else if (p.startsWith('servers/') || p.startsWith('file-ops-rs/')) {
      assign(id, 'layer-sdk-servers');
    } else if (p.startsWith('hooks/')) {
      assign(id, 'layer-runtime-hooks');
    } else {
      assign(id, 'layer-tooling');
    }
    continue;
  }

  // FILE, FUNCTION, CLASS
  const routePath = path || '';

  if (routePath.startsWith('src/archon/')) {
    assign(id, 'layer-core-engine');
  } else if (routePath.startsWith('hooks/')) {
    assign(id, 'layer-runtime-hooks');
  } else if (routePath.startsWith('webapp/')) {
    assign(id, 'layer-ui');
  } else if (routePath.startsWith('vscode-extension/')) {
    assign(id, 'layer-tooling');
  } else if (routePath.startsWith('sdk/')) {
    assign(id, 'layer-sdk-servers');
  } else if (routePath.startsWith('servers/') || routePath.startsWith('file-ops-rs/')) {
    assign(id, 'layer-sdk-servers');
  } else if (routePath.startsWith('scripts/')) {
    assign(id, 'layer-tooling');
  } else if (routePath.startsWith('tests/')) {
    assign(id, 'layer-tooling');
  } else if (routePath.startsWith('skills/') || routePath.startsWith('agents/') || routePath.startsWith('bundles/') || routePath.startsWith('synapses/') || routePath.startsWith('pipelines/')) {
    assign(id, 'layer-component-library');
  } else {
    assign(id, 'layer-tooling');
  }
}

const assigned = Object.keys(nodeLayerMap).length;
const unassigned = nodes.map(n => n.id).filter(id => !nodeLayerMap[id]);

console.log('Assigned:', assigned);
console.log('Unassigned:', unassigned.length);
if (unassigned.length > 0) {
  console.log('Unassigned sample:', unassigned.slice(0, 5));
}

const layerCounts = {};
for (const [id, layerId] of Object.entries(nodeLayerMap)) {
  layerCounts[layerId] = (layerCounts[layerId] || 0) + 1;
}

console.log('\nLayer counts:');
layers.forEach(l => console.log(l.order, l.label + ':', layerCounts[l.id] || 0));

const output = { layers, nodeLayerMap };
fs.writeFileSync('C:/Users/tahaa/Archon/.understand-anything/intermediate/architecture.json', JSON.stringify(output, null, 2), 'utf8');
console.log('\nWritten to architecture.json');
