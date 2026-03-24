# Agents

Formal agent definitions with personas, skill bindings, and handoff protocols.

## Template

See [`_template/`](_template/) for the agent template.

## Agent Index

| Agent                 | Role                    | Skills                                                | Handoff Targets          |
| --------------------- | ----------------------- | ----------------------------------------------------- | ------------------------ |
| spec-writer-agent     | Specification Architect | spec-writer, prompt-architect                         | implementer-agent        |
| implementer-agent     | Implementation Engineer | implementer                                           | reviewer-agent           |
| reviewer-agent        | Compliance Reviewer     | reviewer                                              | implementer-agent (loop) |
| debugger-agent        | Debug Investigator      | systematic-debugging                                  | implementer-agent        |
| ux-research-agent     | UX Researcher           | ux-research                                           | wireframe-agent          |
| ui-design-agent       | Visual Designer         | ui-visual-design, frontend-design                     | design-reviewer-agent    |
| qa-master-agent       | QA Engineer             | e2e-testing-patterns, qa-test-planner, webapp-testing | reviewer-agent           |
| context-curator-agent | Context Architect       | context-curator                                       | dynamic (per pipeline)   |
| dissector-agent       | Codebase Analyst        | dissector                                             | skill-factory pipeline   |
| security-reviewer-agent | Security Reviewer     | security-review, security-awareness synapse           | implementer-agent (loop) |
