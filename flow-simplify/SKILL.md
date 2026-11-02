---
name: flow-simplify
description: "Review and clean up an explicitly scoped diff for reuse, quality, and efficiency before committing. The main session sets scope and checkpoint; a simplifier fixes clear issues without committing."
---

# Flow Simplify

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Review in-scope changes for **reuse, quality, and efficiency** before committing. The main session sets scope/timing; a simplifier performs cleanup.

## Timing and scope

Read `docs/agents/commit-strategy.md` rather than relying on the user to trigger this manually:

| Strategy | Trigger | Scope |
|----------|---------|-------|
| per-ticket | Before each ticket commit | This ticket's uncommitted diff |
| squash | Before the feature's combined commit | Changes from the feature base to the working tree |

The feature base is the feature/main (or master) merge base, e.g. `git merge-base main HEAD`. Include this feature's changes rather than unrelated main updates. If main changed substantially, consider rebasing before the review to keep its scope clear.

The user may also request cleanup directly; use their scope or infer it from `git diff`.

## Core disciplines

1. The main session orchestrates scope and the human checkpoint; the child reviews/fixes.
2. Make surgical changes inside the diff, not surrounding refactors.
3. The child never commits. The main session handles the authorized commit after presenting results.

## Workflow

### Step 1: Set scope

Use the commit strategy and trigger above. Ask if the scope remains ambiguous.

### Step 2: Run cleanup

Read `docs/agents/execution-mode.md`. If missing/invalid rather than `subagent` or `inline`, default to subagent and advise checking configuration. A task-specific override takes precedence.

Apply the user-selected model through the [shared model rules](../_agents/workflow-contract.md#基础模型); inline execution keeps the main-session model.

In subagent mode, dispatch a simplifier with the diff scope. It reads the changes, reviews reuse/quality/efficiency, fixes clear issues, reports debatable tradeoffs instead of applying them, reruns relevant checks, and reports findings/fixes/deliberate exclusions. **It does not commit.**

In inline mode or an explicit override, the main session follows `_agents/simplifier.prompt.md`, including its review dimensions and exclusions.

The role prompt is the sole execution source for both modes; only the executor changes.

### Step 3: Human checkpoint

Show the cleanup report and **wait for user confirmation** before the caller (`/flow-do` or the user) commits.

## Review dimensions

Reuse, quality, efficiency, and exclusions are defined once in `_agents/simplifier.prompt.md`. Check that the report covers them and explains deliberate exclusions.

## Outputs

- In-scope fixes.
- Findings/fixes and deliberate exclusions with reasons.

## Boundaries

| Appropriate | Inappropriate |
|-------------|---------------|
| Pre-commit cleanup | Large refactors needing their own Spec/tickets |
| Reuse/quality/efficiency within the diff | Out-of-scope changes |
| per-ticket or squash scopes | No changes to review |

## Related stages

`/flow-do` invokes this at the configured commit point. The human checkpoint remains before committing. This skill reviews code quality; `/flow-do` also checks fidelity to the Spec and standards.
