---
name: to-plan
description: "Build an implementation blueprint between a confirmed Spec and ticketing. Save local plan.md or an independent remote Plan issue, settle technical choices, paths and risks, and obtain user approval before execution tickets."
---

# To Plan

Follow the target project’s interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

## When to use

- The Spec has been confirmed through `/to-spec`.
- Technical choices and an implementation path must be settled before `/to-tickets`.
- The user wants to review the approach before tickets and implementation.

## Core disciplines

1. **Separate decisions.** The Spec owns product intent and boundaries. The plan settles technical choices, algorithms, and implementation paths for ticketing and implementation.
2. **Review before ticketing.** The user must approve the plan before `/to-tickets`. Reuse explicit approval already given for the current approach.
3. **One current plan.** Update the same local `plan.md` or independent remote Plan issue body. Do not create plan-vN or keep the current approach in Spec comments. Record reasons for changes in the change history.
4. **Expose uncertainty.** Distinguish facts, choices, and assumptions to verify. State each risk's impact and validation method; do not present untested assumptions as conclusions.

## Workflow

### Step 0: Locate the tracker and existing references

Read `docs/agents/issue-tracker.md` and the [shared workflow contract](../_agents/workflow-contract.md#tracker-产物与-plan-引用). Locate this Spec's file/issue reference and existing `Plan:`. Reuse an existing Plan issue rather than creating duplicates on retries or amend. If the tracker declaration is missing, request initialization; do not choose comments or local storage yourself.

### Step 1: Reuse or gather code context

Reuse the `/to-spec` context brief: usually `.scratch/<feature-slug>/context.md` locally, or linked material remotely. If it is missing and more code detail is needed, use `scout` according to execution-mode. A temporary brief is not a second authoritative copy of a remote plan.

### Step 2: Draft the implementation blueprint

Save the plan body as a local file or independent issue according to the tracker. Write it as follows:

- **Lead with the approach, then explain why.** Briefly state how to implement, what to reuse, and where the main changes go. Link product background to the Spec rather than repeating the requirements.
- **Use concrete actions and outcomes.** For example, “保留现有 CSV 调用，增加 JSON 输出”. Avoid vague statements whose scope cannot be assessed.
- **State each fact once.** Explain technical choices in the decision table and reference them from packages. Centralize file and method locations in change anchors; other fields should add distinct information.
- **Expand only where useful.** Compare real alternatives with actual tradeoffs. Do not invent options to fill the table or repeat reuse points, extra files, or risks that add no information.

Bracketed text below is authoring guidance; remove it from the final body.

```markdown
# <Feature> 实施蓝图

Parent: <current Spec file or issue reference>
Spec: <current Spec file or remote version reference>
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

- Packages describe deliverables, technical choices, implementation paths, and risks.
- Tickets own test seams, specific cases, execution scope, and engineering completion criteria.
- Keep rationale in the plan and reference it from tickets. Detailed execution and tests belong to tickets.
- Anchors describe locations and behavior, without line numbers, code, or pseudocode. Check existing attachment points before work; check targets after the responsible ticket or prerequisite creates them. Targets assigned to later tickets need not exist yet. For new modules without existing methods, name a real module/directory attachment point.
- **Change anchors are the sole location source.** Method names belong only in the plan's change-anchor field; tickets reference the file/issue and P<N> through `Plan:` without copying methods. If amend or implementation Step 3.5 detects unexpected renames/moves, update anchors in place, preserving agreed targets and their creation phase. Do not mistake not-yet-implemented targets for stale anchors.

**Package-to-ticket mapping defaults to 1:1 and allows 1:N.** Local tickets use `Plan: plan.md#P<N>`; remote tickets use `Plan: <Plan issue reference> / P<N>`. Keep the Spec version in its separate `Spec:` field.

### Step 3: Cover risks and validation

- Describe package risks in their packages; place cross-package risks after package decomposition. Label untested judgments and state what evidence would confirm them.
- Explain how to validate the overall approach, including critical paths, compatibility, and cross-module boundaries. Tickets add concrete test cases.

### Step 4: Save a reviewable draft

Save the draft before presenting it:

- **Local:** Write `.scratch/<feature-slug>/plan.md`. Backlink `Plan: plan.md` from the current Spec, update `INDEX.md` and the feature entry in `.scratch/README.md`, and preserve historical Specs and registered tickets.
- **GitHub/GitLab:** Create or update the **independent Plan issue body** through the declared tracker tool. Link the current Spec and backlink the returned Plan reference from the Spec body. Migrate plans previously kept only in comments according to the shared contract, retaining historical evidence.
- Follow the [ownership and navigation rules](../_agents/workflow-contract.md#归属层级与列表展示) for `Parent:`. On GitHub, make the Plan a native sub-issue of the Spec, with a `[Plan]` title and the relevant type label. Query and reuse relationships on retries. Report capability, permission, or parent conflicts; Markdown links alone do not prove native synchronization.
- Under the [functional acceptance rules](../_agents/workflow-contract.md#功能验收与票级关闭), the Plan owns functional acceptance, initially `Acceptance: pending`. If the current Spec already owns acceptance records, move them into the same Plan and leave an entry link in the Spec. Preserve evidence and avoid two independent states.
- Mark the body `**状态**: 待 review`. Existing explicit approval of this approach may be recorded directly as 已批准, without asking again. Otherwise save the draft and wait for review; do not create tickets.

Present an accessible file/issue reference and highlight:

- The recommended approach and principal tradeoffs.
- Package deliverables, ordering, and dependencies.
- Decisions still open and risks needing verification.

Focus the review summary on what affects approval, referencing the relevant entries. Do not repeat the whole plan at its end.

**User approval is required before `/to-tickets`.** Requested changes update the same file/issue body for another review. Never create tickets before approval.

### Step 5: Save and hand off

- Update the same plan file/issue body, preserving `Parent:`, `Spec:`, and relationships. Record `**状态**: 已批准（<日期>）` and approval evidence. The local INDEX stores navigation, not a copy of the approval stamp.
- Approach approval permits implementation only. Keep `Acceptance` awaiting actual user functional acceptance; closed tickets or permission to commit do not make it accepted.
- Preserve existing acceptance state and confirmation records. Reset to pending under amend rules only when confirmed functional/acceptance scope changes, not because the skill reran or its template was reapplied.
- Hand `/to-tickets`, `/implement`, and `/find` the actual plan file/issue reference, not only the Spec or a discussion comment.
- Backlink tickets into the plan and update the local INDEX or native sub-issue list. `/amend` maintains the same body; comments hold discussion and change records only.

## What belongs in the plan

| Include | Leave elsewhere |
|---------|-----------------|
| Technical choices: libraries, algorithms, paths | Product intent, boundaries, non-goals → Spec |
| Implementation overview and risks | Seams, test cases, file line details → tickets |
| Cross-package technical decisions | Individual test cases → tickets |

## Boundaries

| Use this skill | Use another path |
|----------------|------------------|
| The Spec is confirmed and the approach needs planning | Unaligned requirements → `/grill-with-docs` |
| The approach needs user review before implementation | One-ticket small changes → `/to-tickets`, no plan required |

## Related stages

- **Input:** Product Spec, optionally the `/to-spec` code-context brief.
- **Output:** Local `plan.md` or an independent Plan issue with method-level change anchors, consumed directly by ticketing and implementation.
- **Amend:** Update the same technical body and anchors as methods move or change names. Keep the tracker's Spec-version convention and synchronize the Plan's `Spec:` reference.
- **Correct the Spec:** If implementation shows that a product decision is technically infeasible, do not improvise around it. Follow the understanding-correction path in `/implement` Step 3.5, revising the Spec so product intent and technical reality agree.
