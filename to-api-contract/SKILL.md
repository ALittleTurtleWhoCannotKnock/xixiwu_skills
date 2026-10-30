---
name: to-api-contract
description: "Extract code- and test-backed HTTP contract fragments for a just-completed backend ticket, especially projects without generated API documentation. The main session confirms scope; a contract-writer handles extraction."
---

# To API Contract

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Extract a contract fragment from completed backend work for frontend-agent integration. The main session confirms scope; a contract-writer extracts it.

## When to use

- A backend ticket is finishing, usually within `/implement`.
- It adds or changes externally exposed HTTP endpoints.
- A frontend agent needs the contract for integration.

## Core disciplines

1. **One ticket, one fragment.** Cover that ticket's endpoints rather than the entire API.
2. **Write for agents.** Prefer precise structure over narrative presentation.
3. **Derive from code/tests**, not memory or invention.
4. **Regenerate when interfaces change.**

## Workflow

### Step 1: Confirm endpoint scope

Read the ticket criteria and list the endpoints it added or changed. Example:

```
本 ticket 涉及的端点：
- POST /posts/:id/comments（新增）
- GET /posts/:id/comments（新增）
```

Exclude unrelated endpoints.

### Step 2: Extract the contract

Read `docs/agents/execution-mode.md`. If missing/invalid rather than subagent/inline, default to subagent and advise checking configuration; respect a task-specific override.

Use the selected model under the [shared model rules](../_agents/workflow-contract.md#基础模型); inline execution keeps the main-session model.

In subagent mode, pass the contract-writer the ticket id/slug and criteria, feature slug for the output path, and route/validation/test locations.

It derives the contract in priority order: **tests → routes → types/validation → error handling**. Write `.scratch/<feature-slug>/contracts/<ticket-slug>.md`, one file per ticket and one block per endpoint. Every field must trace to code/tests; stop and ask if evidence is missing rather than inventing it.

In inline mode or an explicit override, follow `_agents/contract-writer.prompt.md` directly for extraction and block format. That role prompt is the sole execution source in both modes.

Contracts follow the same tracker as Specs/tickets. Local mode uses `.scratch/<feature-slug>/contracts/`; for a remote tracker, attach to the issue or use its declared contract-storage convention.

### Step 3: Review the fragment

Check that it covers only this ticket's endpoints, that error codes match the values the frontend branches on, and that types/required fields match validation.

### Step 4: Regenerate after changes

If paths, fields, or error codes change, regenerate affected ticket fragments, update the generation date, and add `**变更说明**: <what changed>`.

If frontend integration finds a response/contract mismatch, report that the contract may be stale and regenerate the affected fragment.

## Output

`.scratch/<feature-slug>/contracts/<ticket-slug>.md`, covering this ticket's endpoints.

## Boundaries

| Appropriate | Inappropriate |
|-------------|---------------|
| Projects without generated API docs, such as Node.js backends | OpenAPI/tRPC/GraphQL sources that can export their contract directly |
| Just-completed backend work | Reconstructing old work without rereading/verifying source |
| Frontend/backend agent integration | Internal functions without external endpoints |

## Related stages

`/implement` triggers this for a backend endpoint ticket. Paths correspond to `/to-tickets`. Use `/diagnosing-bugs` to determine whether integration mismatches come from a stale contract or an implementation bug.
