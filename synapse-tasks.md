# OMNISKILL Synapses — Implementation Tasks

## Section 1: Core Synapse Framework
- [X] T001 [P] Create `synapses/_template/SYNAPSE.md`
- [X] T002 [P] Create `synapses/_template/manifest.yaml`
- [X] T003 [P] Create `synapses/metacognition/SYNAPSE.md`
- [X] T004 [P] Create `synapses/metacognition/manifest.yaml`
- [X] T005 [P] Create `synapses/metacognition/resources/confidence-rubric.md`
- [X] T006 [P] Create `synapses/metacognition/resources/reflection-template.md`
- [X] T007 [P] Create `synapses/metacognition/resources/stuck-detection.md`
- [X] T008 [P] Create `schemas/synapse-manifest.schema.yaml`

## Section 2: Registry Integration
- [X] T009 Update `omniskill.yaml` — add `synapses:` section
- [X] T010 Update `src/omniskill/core/registry.py` — add Synapse dataclass + parsing + lookup

## Section 3: CLI Commands
- [X] T011 Update `src/omniskill/commands/list_cmd.py` — add synapses to COMPONENT_TYPES + listing
- [X] T012 Update `src/omniskill/commands/info.py` — add synapse type handling
- [X] T013 Update `src/omniskill/commands/validate.py` — add `_validate_synapse()` function
- [X] T014 Update `src/omniskill/commands/doctor.py` — add synapse count
- [X] T015 Update `src/omniskill/commands/install.py` — add `--synapse` option

## Section 4: Adapters
- [X] T016 Update `adapters/base.py` — add `read_synapse()`, `get_synapse_target_path()`, `install_synapse()`
- [X] T017 Update `adapters/cursor/adapter.py` — override synapse target path
- [X] T018 Update `adapters/windsurf/adapter.py` — override synapse target path

## Section 5: Schema Extensions
- [X] T019 Update `schemas/agent-manifest.schema.yaml` — add `synapse-bindings` field
- [X] T020 Update `schemas/pipeline.schema.yaml` — add `synapse-checkpoint` + `synapse-mode` fields

## Section 6: Agent Integration
- [X] T021 Update ALL 8 agent AGENT.md files — add metacognition synapse binding section

## Section 7: Pipeline Integration
- [X] T022 Update ALL 5 pipeline YAML files — add synapse checkpoint steps

## Section 8: VS Code Extension
- [X] T023 [P] Create `vscode-extension/src/views/synapsesTree.ts`
- [X] T024 [P] Create `vscode-extension/src/webviews/synapseDetailPanel.ts`
- [X] T025 Update `vscode-extension/src/types.ts` — add Synapse types
- [X] T026 Update `vscode-extension/src/extension.ts` — register tree provider
- [X] T027 Update `vscode-extension/src/commands.ts` — register commands
- [X] T028 Update `vscode-extension/src/cli.ts` — add listSynapses function
- [X] T029 Update `vscode-extension/package.json` — add view, commands, menus

## Section 9: Web App
- [X] T030 [P] Create `webapp/src/app/synapses/page.tsx`
- [X] T031 [P] Create `webapp/src/app/synapses/[slug]/page.tsx`
- [X] T032 Update `webapp/src/data/registry.json` — add synapses data
- [X] T033 Update `webapp/src/lib/types.ts` — add Synapse type
- [X] T034 Update `webapp/src/lib/registry.ts` — add synapse functions
- [X] T035 Update `webapp/src/components/Navbar.tsx` — add Synapses nav link
- [X] T036 Update `webapp/src/app/page.tsx` — add synapse stats + feature card

## Section 10: Documentation
- [X] T037 [P] Create `docs/creating-synapses.html`
- [X] T038 [P] Create `docs/creating-synapses.md`
- [X] T039 Update sidebar in ALL existing `docs/*.html` files (10 files)
- [X] T040 Update `README.md` — add synapse section, directory structure, feature list
