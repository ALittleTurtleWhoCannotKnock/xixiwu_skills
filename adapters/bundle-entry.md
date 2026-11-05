---
name: dev-flow
description: "Unified development workflow methods and resources: requirements, Spec, Plan, Todos, implementation, debugging, browser verification and progress. Use the agent's permanent role instructions to select permitted stages; this package does not assign a role or restrict tools."
---

# Dev Flow

This is one self-contained distribution of the workflow. The original flow-* names below are internal methods; they do not require separate Skill installs or shell commands. Read only the relevant stage instructions and supporting resources. Relative links resolve from the file containing them, inside this bundle; no external source checkout is required.

## Role before method

Use the agent's permanent host Instructions as its role. Skill attachment supplies methods, not identity, permissions or authority. A display description alone does not configure a role. If no role is configured, explain that this is a method library and ask for the intended role; do not announce that installing this package made you every specialist.

- A configured Flow coordinator uses [Flow role](roles/flow.md), flow-run and flow-status. It delegates specialist work and never selects inline implementation as a fallback for missing workers.
- Specialists use their matching role and bounded assignment: [Requirements](roles/requirements.md), [Planning](roles/planning.md), [Development](roles/development.md), or [Verification](roles/verification.md). They return results/questions to the coordinator.
- A user explicitly running a standalone stage without a configured specialist identity may use that method's normal workflow. This does not reconfigure an existing agent's permanent role.

Carry real human Spec confirmation and scoped delegation, preserve mandatory checks, and keep functional acceptance and Git/deployment authorization separate. Treat role instructions as behavioral boundaries; actual tool/filesystem restrictions depend on the host/runtime.

## Stage methods

{{STAGE_LINKS}}

Shared references: [language policy](_agents/language-policy.md), [workflow contract](_agents/workflow-contract.md), and [diagram guidance](_agents/diagram-guide.md). Host-specific examples remain optional references; use actual host capabilities rather than inventing an API or applying another product's configuration.

On Multica, read the [Multica adapter](flow-run/references/multica.md) before dispatching work. It distinguishes persistent Squad/issue wakeups from ordinary run-owned background work, and permanent role instructions from Skill discovery and actual permissions.
