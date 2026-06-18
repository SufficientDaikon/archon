import json

with open('C:/Users/tahaa/Archon/.understand-anything/intermediate/assembled-graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
nodes = data['nodes']

def get_top(path):
    p = path.replace('\\', '/')
    parts = p.split('/')
    return parts[0] if len(parts) > 1 else '__root__'

def assign_layer(node_id, path, node_type):
    top = get_top(path)
    if top == 'hooks':
        return 'layer:runtime-hooks'
    if top == 'src':
        return 'layer:core-engine'
    if top == 'sdk':
        return 'layer:sdk-cli'
    if top in ('skills', 'agents', 'synapses', 'bundles', 'pipelines'):
        return 'layer:manifests'
    if top in ('webapp', 'vscode-extension', 'servers'):
        return 'layer:tooling'
    if top == 'file-ops-rs':
        return 'layer:core-engine'
    if top == 'scripts':
        return 'layer:sdk-cli'
    return 'layer:config-docs'

node_layer_map = {}
for n in nodes:
    nid = n['id']
    path = n.get('path', n.get('filePath', ''))
    ntype = n.get('type', '')
    node_layer_map[nid] = assign_layer(nid, path, ntype)

layers = [
    {
        'id': 'layer:config-docs',
        'label': 'Configuration & Documentation',
        'description': 'Root-level config files (pyproject.toml, archon.yaml), JSON/YAML schemas, CI/CD pipelines, documentation, prompts, and project-level settings that define and describe the Archon framework.',
        'color': '#6B7280',
        'order': 0
    },
    {
        'id': 'layer:manifests',
        'label': 'Manifest Components',
        'description': 'The declarative component library: skill YAML manifests and SKILL.md docs, agent definitions, synapse configurations, bundle groups, and execution pipeline definitions that form the installable Archon skill catalog.',
        'color': '#8B5CF6',
        'order': 1
    },
    {
        'id': 'layer:runtime-hooks',
        'label': 'Runtime Hooks',
        'description': 'Claude Code hook scripts (session_boot, prompt_router, guard_bash, guard_write, quality_bash, quality_write, completion_gate, agent_context) and shared utilities that inject contextual XML into every Claude Code prompt at runtime.',
        'color': '#F59E0B',
        'order': 2
    },
    {
        'id': 'layer:core-engine',
        'label': 'Core Engine',
        'description': 'The Python engine package (src/archon/) implementing the registry, pipeline state machine, synapse engine v2, policy engine, MCP schema synthesis, and the Rust file-ops library — the computational backbone that powers all Archon operations.',
        'color': '#EF4444',
        'order': 3
    },
    {
        'id': 'layer:sdk-cli',
        'label': 'SDK & CLI',
        'description': 'The public ArchonSDK (sdk/archon.py) exposing validate_* methods for external callers, the Typer CLI entrypoint, and scripts for automation tasks such as graph building and batch processing.',
        'color': '#10B981',
        'order': 4
    },
    {
        'id': 'layer:tooling',
        'label': 'Tooling & Interfaces',
        'description': 'The Next.js dashboard webapp for browsing skills and visualizing the knowledge graph, the VS Code extension for in-editor Archon integration, and the MCP server implementations that expose Archon capabilities to AI agents.',
        'color': '#3B82F6',
        'order': 5
    }
]

output = {
    'layers': layers,
    'nodeLayerMap': node_layer_map
}

out_path = 'C:/Users/tahaa/Archon/.understand-anything/intermediate/architecture.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('Written to', out_path)
print('Total nodes:', len(node_layer_map))

from collections import Counter
counts = Counter(node_layer_map.values())
for layer in layers:
    lid = layer['id']
    lname = layer['label']
    print(f'  {lname}: {counts.get(lid, 0)} nodes')
