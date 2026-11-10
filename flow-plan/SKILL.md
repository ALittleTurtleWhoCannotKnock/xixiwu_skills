---
name: flow-plan
description: "Split a confirmed Spec into one or more independently deliverable Plans, respecting user-specified count/grouping. Settle each scope's approach, paths and checks, save distinct Plan artifacts, and obtain applicable approval before simple Todos."
---

# Flow Plan

Follow the target project’s interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

## When to use

- The Spec has been confirmed through `/flow-spec`.
- Technical choices and an implementation path must be settled before `/flow-todo`.
- The user wants to review the approach before tickets and implementation.

## Core disciplines

1. **Separate decisions.** The Spec owns product intent and boundaries. The plan settles technical choices, algorithms, and implementation paths for ticketing and implementation.
2. **Review before ticketing.** Each Plan needs applicable user approval or explicitly delegated technical review before `/flow-todo`. Reuse valid authorization for the current approach.
3. **One current artifact per Plan scope.** A Spec may have multiple independent Plans. Reuse each scope's existing file/issue, including legacy `plan.md`; do not create plan-vN for a revision or replace several Plans with P<N> packages in one document.
4. **Expose uncertainty.** Distinguish facts, choices, and assumptions to verify. State each risk's impact and validation method; do not present untested assumptions as conclusions.

## Workflow

### Step 0: Locate the tracker and existing references

Read the tracker and [shared contract](../_agents/workflow-contract.md#tracker-产物与-plan-引用). Locate the current Spec and its `Plans:` list or legacy `Plan:` reference; inspect each actual scope, approval, existing Todos and claims. Reuse matching scoped artifacts on retries/amendment. Do not quietly overlap an approved/in-flight Plan or rewrite historical ownership to repartition it. If the tracker declaration is missing, request initialization rather than choosing a new store.

### Step 1: Reuse or gather code context

Reuse the `/flow-spec` context brief: usually `.scratch/<feature-slug>/context.md` locally, or linked material remotely. If it is missing and more code detail is needed, use `scout` according to execution-mode. A temporary brief is not a second authoritative copy of a remote plan.

### Step 2: Choose independent Plan scopes, then draft each blueprint

Apply the [Spec-to-Plans rules](../_agents/workflow-contract.md#Spec与多个Plan). Without an explicit count, the AI chooses one or several Plans from actual functional boundaries and coupling, and briefly explains the count. An explicit user count/grouping wins, including for a small requirement; make that many real Plans. Do not substitute one Plan's P1..Pn for peer Plan artifacts. If independent, nonempty and complete scopes cannot satisfy the request, show the concrete conflict and ask before changing the count or inventing work.

Check that the scopes collectively cover the confirmed requirement without duplicate ownership, each can be implemented/tested from the agreed baseline without another new Plan's output, and shared mutable anchors/contracts will not invalidate a peer. Splitting frontend/backend/testing phases does not establish independence. Settle conflicts before describing the Plans as independent; semantic independence also does not remove host directory locks.

For each selected Plan, prepare the difficult work using the [simple-Todo rules](../_agents/workflow-contract.md#执行任务与Todo). Its implementation outline identifies concrete engineering results that can become simple Todos with known inputs, boundaries and checks. A Todo may cover one focused layer or rule; the Plan owns the complete functional result. Settle consequential product/technical choices or investigate a bounded missing fact before dependent implementation. Routine code steps remain local, and change anchors remain the location source.

Save one body per Plan scope. Use this template for each, not a single document containing all peer Plans:

- **Lead with the approach, then explain why.** Briefly state how to implement, what to reuse, and where the main changes go. Link product background to the Spec rather than repeating the requirements.
- **Use concrete actions and outcomes.** For example, “保留现有 CSV 调用，增加 JSON 输出”. Avoid vague statements whose scope cannot be assessed.
- **State each fact once.** Explain technical choices in the decision table and reference them from packages. Centralize file and method locations in change anchors; other fields should add distinct information.
- **Expand only where useful.** Compare real alternatives with actual tradeoffs. Do not invent options to fill the table or repeat reuse points, extra files, or risks that add no information.

Bracketed text below is authoring guidance; remove it from the final body.

```markdown
# <Feature> 实施蓝图

Parent: <current Spec file or issue reference>
Spec: <current Spec file or remote version reference>
Scope: <owned requirement/acceptance subset and actual Spec references>
**状态**: 待 review
Acceptance: pending

## 方案概述

[Briefly describe the recommended approach: existing capabilities reused, changes introduced, and how the result satisfies the Spec. Link to the Spec for background.]

## 技术决策表

| 决策点 | 选项 | 选择 | 理由 |
|-------|------|------|------|
| [Decision needed] | [Real alternatives] | [Chosen approach] | [Tradeoffs based on existing code and constraints; explain rejected alternatives where useful] |

## 包分解

### P1: <package name, corresponding to one or more tickets>
**交付结果**：[Capability delivered and existing behavior preserved; make scope assessable.]
**技术选择**：[Reference decision-table entries and add only package-specific choices.]
**实现思路**：[Explain the causal implementation path, responsibilities, and connections; leave code and individual test steps to tickets.]
**改动锚点**：
- [Existing attachment point `path#method` → target `path#method`; explain the behavior change and whether this package or a prerequisite P<N> creates the target.]

**其他关键文件**：[Other changed/new files not covered by anchors; omit if none.]
**复用点**：[Additional reuse not already explained; omit if none.]
**风险点**：[Specific risk → impact → verification; reference global risks instead of repeating them.]

### P2: ...

## 功能验收

- [User-confirmed functional acceptance items from the Spec, linked to packages or tickets; track outstanding human experience/device acceptance here.]
- 验收记录：[Actual user confirmation or feedback. If not yet accepted, state that clearly; approach approval is not functional acceptance.]
```

**Content boundaries:**

- A Plan owns an independent functional scope. Its P<N> packages describe that scope's deliverables, technical choices, implementation paths and risks; package numbers are local to that Plan.
- Tickets own test seams, specific cases, execution scope, and engineering completion criteria.
- Keep rationale in the plan and reference it from tickets. Detailed execution and tests belong to tickets.
- Anchors describe locations and behavior, without line numbers, code, or pseudocode. Check existing attachment points before work; check targets after the responsible ticket or prerequisite creates them. Targets assigned to later tickets need not exist yet. For new modules without existing methods, name a real module/directory attachment point.
- **Change anchors are the sole location source.** Method names belong only in the plan's change-anchor field; tickets reference the file/issue and P<N> through `Plan:` without copying methods. If /flow-amend or implementation Step 3.5 detects unexpected renames/moves, update anchors in place, preserving agreed targets and their creation phase. Do not mistake not-yet-implemented targets for stale anchors.

**Each Plan splits into simple Todos; a package may map to one or several.** Local references qualify the owner, e.g. `Plan: plans/import.md#P1` (legacy `plan.md#P1` stays valid); remote references use the actual Plan issue plus P<N>. P1 under a different Plan is not the same package. Keep Spec provenance separate.

### Step 3: Cover risks and validation

- Describe package risks in their packages; place cross-package risks after package decomposition. Label untested judgments and state what evidence would confirm them.
- Explain how to validate the overall approach, including critical paths, compatibility, and cross-module boundaries. Tickets add concrete test cases.

### Step 4: Save a reviewable draft

Save the draft before presenting it:

- **Local:** Reuse each matching Plan's path. Existing `plan.md` remains valid; new peer scopes use `.scratch/<feature>/plans/<scope-slug>.md`. Backlink every actual Plan under the Spec's `Plans:` list (singleton `Plan:` is compatible), and group its own Todos in INDEX. Do not rename old files merely to adopt the new layout.
- **GitHub/GitLab:** Create/update one **independent Plan issue body per scope**, each owned by the Spec. Backlink the complete Plan list from the Spec and list only each Plan's own Todos. Migrate old comment-only plans with history/evidence retained; never treat issue numbers as Plan counts/versions.
- Follow the [ownership and navigation rules](../_agents/workflow-contract.md#归属层级与列表展示) for `Parent:`. On GitHub, make the Plan a native sub-issue of the Spec, with a `[Plan]` title and the relevant type label. Query and reuse relationships on retries. Report capability, permission, or parent conflicts; Markdown links alone do not prove native synchronization.
- Under the [acceptance rules](../_agents/workflow-contract.md#功能验收与票级关闭), each Plan owns its acceptance subset, initially pending unless valid existing evidence applies. Transfer only its items from Spec-owned acceptance, leaving links. Keep genuinely Spec-wide checks at the Spec; do not duplicate the same mutable item or reset another Plan's accepted scope.
- Mark the body `**状态**: 待 review`. Existing explicit approval of this approach may be recorded directly as 已批准, without asking again. Otherwise save the draft and wait for review; do not create tickets.

Present all Plan references with the chosen count/user directive, scope coverage and independence basis, then highlight per Plan:

- The recommended approach and principal tradeoffs.
- Simple-Todo candidates, ordering and dependencies inside this Plan; no hidden prerequisites on peer Plans.
- Decisions still open and risks needing verification.

Focus the review summary on what affects approval, referencing the relevant entries. Do not repeat the whole plan at its end.

**Applicable approach approval is required before a Plan's `/flow-todo`.** Reuse actual delegated automatic review when provided by flow-run; otherwise obtain user approval, which may cover several identified Plans together. A requested count alone is not approach approval. One Plan waiting for review does not block a different approved independent scope.

### Step 5: Save and hand off

- Update each same-scope Plan artifact, preserving Parent/Spec/Scope and relationships. Record its approval and actual evidence independently. INDEX stores navigation, not copies of approval stamps.
- Approach approval permits implementation only. Keep `Acceptance` awaiting actual user functional acceptance; closed tickets or permission to commit do not make it accepted.
- Preserve existing acceptance state and confirmation records. Reset to pending under /flow-amend rules only when confirmed functional/acceptance scope changes, not because the skill reran or its template was reapplied.
- Hand `/flow-todo`, `/flow-do`, and `/flow-status` the actual plan file/issue reference, not only the Spec or a discussion comment.
- Backlink each Todo only under its owning Plan and update INDEX/native relationships. `/flow-amend` updates the same affected Plan bodies while preserving peer scopes; comments hold discussion/change reasons only.

## What belongs in the plan

| Include | Leave elsewhere |
|---------|-----------------|
| Technical choices: libraries, algorithms, paths | Product intent, boundaries, non-goals → Spec |
| Implementation overview and risks | Seams, test cases, file line details → tickets |
| Cross-package technical decisions | Individual test cases → tickets |

## Boundaries

| Use this skill | Use another path |
|----------------|------------------|
| The Spec is confirmed and the approach needs planning | Unaligned requirements → `/flow-clarify` |
| The approach needs user review before implementation | One-ticket small changes → `/flow-todo`, no plan required |

## Related stages

- **Input:** Product Spec, optionally the `/flow-spec` code-context brief.
- **Output:** One or more independently scoped Plan files/issues with distinct identity, approval/acceptance and change anchors, plus the Spec's full Plan list.
- **/flow-amend:** Update affected Plan bodies/anchors and provenance in place. Preserve unaffected scopes under the shared version-applicability rules; do not treat every Spec version bump as a new Plan set.
- **Correct the Spec:** If implementation shows that a product decision is technically infeasible, do not improvise around it. Follow the understanding-correction path in `/flow-do` Step 3.5, revising the Spec so product intent and technical reality agree.
