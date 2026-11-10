---
name: flow-do
description: "Implement and validate a confirmed ticket using appropriate checks and reused tests. The main session reviews evidence and automatically closes engineering-complete tickets; human functional acceptance stays in Plan/Spec and Git commits remain separately authorized."
---

# Flow Do

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Implement and validate tickets. The main session orchestrates decisions/review; an implementer performs execution unless inline mode is selected.

## When to use

Tickets are confirmed, an executable ticket exists, and code/configuration/documentation must be changed.

## Core disciplines

1. Separate orchestration from execution.
2. Match validation to the change and reuse tests rather than creating files per ticket.
3. Execute settled decisions; report uncovered blocking decisions rather than guessing.
4. Technical choices belong to the plan, product boundaries to the Spec, and execution details to the ticket; confirmed small tickets contain intentionally omitted decisions.
5. If the plan cannot meet a product decision, use Step 3.5 understanding correction rather than silently deviating.
6. Child agents never commit; the main session owns commit cleanup/checkpoints.
7. Never commit or push without explicit user authorization, even when checks pass.

## Workflow

Read the [shared contract](../_agents/workflow-contract.md) and target tracker declaration before interpreting fields, states, or dependencies.

### Step 1: Select and claim

Select a ticket with all declared blockers satisfied. The current flow releases dependencies on resolved; legacy code-complete follows only declared compatibility semantics and engineering evidence. Verify independent external conditions separately. Follow Spec/Plan references; an explicit none with a reason uses the confirmed small-ticket decisions, not missing-document requests.

Read the Todo's exact owning Plan file/issue and qualified P<N>, its Scope and actual approval. A peer Plan with the same package number or an approved neighboring scope is not a substitute. Closed state is not approval; do not use a stale copy/comment instead of the authoritative body.

Before execution, change ready to claimed in the tracker and record the executor (locally `By: <agent/user>` may accompany Status). Do not take another executor's claim; only explicitly confirmed stale claims may be reassigned.

For multiple Spec versions, verify the selected Plan's current applicability from the Spec/INDEX registry and its scope/version evidence. An unaffected earlier binding may remain valid only with explicit unchanged-scope provenance; do not reject it or reimplement completed work solely for a global version bump. Changed/uncertain scope blocks only work relying on that unresolved provenance, not unrelated approved Plans.

Resolve the [functional acceptance owner](../_agents/workflow-contract.md#功能验收与票级关闭): Plan, otherwise Spec. Separate human functional acceptance from engineering checks. Align completion conventions before adopting the new flow without resetting historical states. If the user is confirming functional acceptance and no execution work remains, go directly to Step 6 rather than redoing closed tickets.

### Step 2: Confirm validation and existing test locations

Use the [shared validation rules](../_agents/workflow-contract.md#验证方式与测试组织):
- Locate the framework, matching seams/files, fixtures, and commands first.
- Use behavior tests for behavior/API/bugs, before/after regression for pure refactors, and applicable checks for docs/config/styles rather than artificial failures.
- Record the strategy and test locations; parameterize related cases, explaining genuinely necessary new files.
- Fill missing behavior-test boundary decisions; reuse existing authorization. Explain checks for non-runtime changes without inventing seams.

### Step 3: Execute and validate

Before assigning implementation, the stage supervisor checks the [execution task](../_agents/workflow-contract.md#执行任务与Todo): can the executor identify its first action, prepared inputs, bounded result and completion checks without inventing product rules or choosing the feature architecture? If not, refine the task or return the consequential gap to its owner before dispatch. The supervisor may prepare several settled tasks for one Todo or group related small Todos; keep their ordinary internal execution in the same context when useful, without a Flow Agent round trip per step.

Read execution-mode. Missing/invalid subagent/inline configuration defaults to subagent with a configuration notice; honor a task override. Apply the [selected-model rules](../_agents/workflow-contract.md#基础模型); inline keeps the main-session model.

In subagent mode, send the implementer:
- The specific execution task(s): result, available inputs and settled rules, prerequisites, permitted change boundary, and task-level completion checks/examples.
- The current ticket reference/body, criteria, and blockers.
- The shared contract and tracker state declaration, unless the adapter already appended the contract.
- The exact owning Plan/Scope/P<N>, decisions, risks, and existing/target anchors. If intentionally omitted, use the ticket decisions and skip plan-anchor checks.
- The applicable Spec version, seams and boundaries, including current unchanged-scope provenance for an earlier binding, or confirmed small-ticket equivalents.
- Commit-strategy path, validation approach, code/test/fixture locations, and required commands.
- The upper acceptance entry and pending human items, separated from mandatory ticket engineering checks.

The implementer verifies blockers, executes only the prepared scope, reuses tests, implements/validates and reviews its diff. Inspect its result against the assigned task before advancing the sequence. An internal task may be complete while the Todo still has required work: keep the Todo incomplete until all its engineering criteria pass. Resolve consequential missing decisions with their owner before redispatching. A reported wrong technical direction follows Step 3.5 rather than blind retries or abandonment.

Inline execution follows `_agents/implementer.prompt.md` directly. The same prompt/shared validation contract governs both modes.

### Step 3.5: Correct a wrong direction

Use when the ticket's technical approach conflicts with actual architecture or when an anchor that should already exist has unexpectedly moved/disappeared. A future target not yet due is not an error; honor its creation phase.

1. Inspect actual architecture, channels, flow, and boundaries. Explain why the assumption fails; locate unexpectedly renamed/moved symbols.
2. Update the owning Plan's technical entry/anchors first, or the small ticket's decisions when no plan exists. Revise affected ticket scope/criteria and add the old assumption, correction, and architectural evidence. Do not duplicate method anchors into the ticket or reset unrelated Plans.
3. Determine whether to revise the Spec:

| Correction | Meaning | Spec action |
|------------|---------|-------------|
| Understanding correction | Changes how the approach really works: channel, responsibility, or flow | Must update the Spec |
| Implementation detail | Names/parameters/internal structure without changed meaning | Keep in ticket/plan |
| New constraint/boundary | Compatibility, debouncing, validation, etc. | Update Spec if it affects later work or requirement understanding |

If the plan is technically unable to satisfy a product decision, report the conflict and obtain user confirmation before changing that product decision. Update the same plan body too.

4. For understanding corrections/necessary constraints, update the current Spec's approach, business flow, sequence, or decisions. Write locally or to the authoritative remote body; technical plan corrections stay in the independent Plan body, not Spec comments. Example stamp:

```
> 修正（ticket NN）：[一句话说明修正内容 + 依据]。原理解 [X] 在现有架构不成立，修正为 [Y]。
```

This corrects a still-working Spec in place, without a new version. `/flow-amend` versions already implemented requirements.

5. Redispatch the corrected ticket. If the same ticket produces direction errors on **two consecutive attempts**, stop automatic correction/redispatch. Request human alignment or a return to `/flow-spec`; do not loop indefinitely.

### Step 4: Review engineering completion

Check the report on two axes:

**A. Completion:** Does code satisfy this ticket's scope and engineering criteria? Hand outstanding product/experience/functional-device acceptance to Plan/Spec with provenance; it does not block an engineering-complete ticket. Required engineering checks must actually pass; explain inapplicable checks. Review test reuse, justified additions, cleaned temporary probes, and real behavior coverage at the agreed seam.

**B. Evidence-based findings:**

| Severity | Meaning | Action |
|----------|---------|--------|
| P0 | Blocks completion: Spec conflict, failed tests, or drift | Fix before closing |
| P1 | Should fix before release: concrete smells/boundary gaps | Record and decide whether to fix now |
| P2 | Informational/readability note | Record without blocking |

Check drift against both product and technical decisions. Treat deviations as P0 and confirm whether to fix implementation or explicitly revise decisions. Invent no findings; state that there are no blockers when appropriate. Return P0/P1 for correction or a user decision.

**After each ticket, without waiting for human acceptance or a commit:**
- For external HTTP endpoints, first generate required `/flow-api` deliverables for integration.
- When implementation, mandatory engineering checks, review, and required artifacts pass, the main session writes `Status: resolved`. Locally retain evidence; remotely call close and reread native state. Do not request per-ticket user acceptance.
- Register remaining human functional items in Plan/Spec, or the shared small-change handoff when both are omitted. Failed/unrun engineering checks remain claimed and cannot be moved upward to justify closure.
- Record commands/results, change location, and Git facts; release dependencies and continue eligible work. If native close fails, report engineering complete/native still open and the actual cause; do not claim closure or reimplement passed work.

### Step 5: Cleanup and commit independently

Read commit-strategy; if absent, request initialization. Per-ticket handles a commit point after each Step 4; squash handles it after all execution tickets resolve. Parked, unknown, or failed work is not complete.

Commit/push still requires explicit authorization. If the user defers committing, or this task is not preparing a commit, leave the working tree and record the later Git work. Do not force cleanup or a Git checkpoint merely to close tickets; continue eligible engineering work.

When preparing a commit, reuse existing explicit authorization:
1. Invoke `/flow-simplify` under execution-mode, scoped by commit-strategy and the user's limits.
2. Rerun checks after cleanup and regenerate changed contracts. Reopen affected tickets and recheck downstream dependencies on actual engineering regression; human functional checks stay above.
3. Present results and handle the human commit checkpoint. Commit only when explicitly authorized; otherwise preserve changes.
4. A deferred commit does not undo Step 4 closure. Reopen only for actual engineering issues. Keep Git, ticket completion, and functional acceptance distinct.

### Step 6: Upper-level functional acceptance

After execution tickets finish, hand the user the Plan/Spec acceptance entry and pending items. Show engineering complete/awaiting functional acceptance; keep pending and the parent open until actual user confirmation.

On explicit acceptance, check the current version and engineering completion, record accepted plus evidence at the single owner, then close that acceptance item. Approach approval or Git authorization is not acceptance. Feedback records changes-requested and leads to scoped follow-on/regression tickets. Missing records remain unknown rather than inferred from closed tickets.

## Outputs and completion

Deliver verified changes, maintained useful coverage, review/cleanup results, actual ticket/closure state, Git authorization/working-tree facts, and any required contract fragments. A ticket is resolved by engineering completion; a feature is accepted by explicit user functional confirmation; a commit follows its separate authorization/checkpoint.

When the user requests a local browser test pass after Do, `/flow-e2e` reuses this handoff and the relevant Todo/Plan/Spec to start or reuse the app and exercise the completed feature. It does not require creating a regression suite or run automatically after every Todo.
