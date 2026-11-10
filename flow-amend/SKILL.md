---
name: flow-amend
description: "Handle confirmed changes to an implemented feature with an incremental Spec version, scoped updates to affected Plans and follow-on Todos. Preserve independent unaffected Plans and check whether the change requires redesign."
---

# Flow Amend

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Evolve an implemented feature incrementally from its existing Spec rather than restarting the entire workflow.

## When to use

- Existing Spec/Todos were implemented; Git commit status is tracked separately.
- Fields, behavior, boundaries, or local requirements change.
- Repeating the complete requirements workflow would be disproportionate.

## Core disciplines

1. Ask only about the changed part.
2. Distinguish an increment from a redesign; small patches must not conceal a fundamental change.
3. Freeze old Specs; write a separate version such as spec-v2.md.
4. Use the latest execution version, referring to history as needed.
5. Reuse each affected scoped Plan artifact, not plan-vN or Spec comments; preserve unaffected peer Plans.
6. Before classifying depth, briefly steelman the change's true intent: restate it, examine both directions, and find decisive variables. Apply the global AGENTS.md significance criteria, including architecture, scope, cross-module impact, alternatives, user behavior, and irreversibility.

## Workflow

### Step 1: Read current state

Read the [shared contract](../_agents/workflow-contract.md), tracker, and execution-mode (missing defaults to subagent for later scout work).

Read INDEX/current Spec and all `Plans:` or legacy `Plan:` references, their Scope/version bindings, own Todos and existing approval/acceptance. Identify which confirmed change affects which Plan's requirements, contracts or mutable anchors; do not treat all peers as affected by default. Record unchanged-scope evidence for peers carried forward under an earlier binding. Missing local .scratch does not imply a remote artifact is absent. If no Spec is locatable, use the requirements workflow.

### Step 2: Discuss only the change

Do not repeat unchanged requirements. Example:

```
当前 spec-vN 的方案是 X。你说要变动，具体变什么？

- 哪个决策/模块/字段要改？
- 改成什么？
- 为什么变？（新需求 / 原方案有问题 / 外部约束变了）
```

### Step 3: Confirm depth

Classify depth for the affected scope. A redesign inside one independent Plan does not by itself invalidate unrelated Plan scopes; verify actual shared contracts/anchors before expanding the impact or resetting peer approval/acceptance.

Classify the change and present the judgment:

| Depth | Signals | Action |
|-------|---------|--------|
| Surface | Fields, copy, boundary checks, defaults | New Spec version and follow-on tickets |
| Local | One implementation choice, library, or module responsibility | Incremental version and tickets |
| Fundamental | Architectural assumptions, main flow, non-goals, or most decisions overturned | Stop incremental work and recommend `/flow-spec` |

For a fundamental change, explain the concrete issue, for example:

```
这个变动动摇了 spec 的核心决策（具体：[哪条]）。
在原 spec 上打补丁会在烂地基上续建。
建议：重新走 /flow-spec 生成全新 spec。
仍要强制增量吗？（不推荐）
```

Continue only after the user's confirmation.

### Step 4: Write the next Spec

For an increment, create local `spec-v(N+1).md`; remotely retain the tracker's existing version-storage convention and older references. Do not silently change how versions are stored.

```markdown
# <Feature> Spec v(N+1)

Parent: <沿用已确认的 Epic；没有则 none>
Plans: <全部适用 Plan 的真实引用与负责范围；无则 none，旧单 Plan: 兼容>

> 本版本是对 v(N) 的增量变更，只记录变动点。完整背景见 v(N)。

## 本次变动（v(N) → v(N+1)）

### 变动的决策
| 决策点 | v(N) | v(N+1) | 理由 |
|-------|------|--------|------|
| [决策] | [原方案] | [新方案] | [为什么变] |

### 变动的模块影响
[文字列出新增/修改/不受影响的模块与原因]

### 变动的功能流程（如涉及）
[参照 diagram-guide，用 flowchart 画受影响的业务路径、判断与结果，标明与原流程的衔接；无变化时明确沿用旧版流程]

### 变动的时序（如涉及）
[参照 diagram-guide 时序图规范，只画受影响的调用段]

## 不变的部分
以下内容沿用 v(N)，未变动：
- 问题陈述、非目标
- 未列在上方"变动的决策"中的所有决策
```

Record changed points only and explicitly inherit unchanged parts from v(N); do not copy the entire earlier Spec.

### Step 5: Update the current-version entry

Create/update local INDEX's current version and evolution history while retaining the Plan/ticket [navigation hierarchy](../_agents/workflow-contract.md#归属层级与列表展示). Do not replace it with a version-only list.

```markdown
# Feature: <feature>

**当前版本**: [spec-v(N+1).md](spec-v(N+1).md)（执行前核对本版本及各 Plan 的适用范围／版本）

Plans: <保留所有适用 Plan 及其当前范围／版本引用；旧 plan.md 可继续使用>

## 层级
[保留既有链接，标记当前规格及历史票版本；Step 6 保存新票后追加其真实链接，不重复保存状态]

## 演进
- v1 (spec.md): [一句话概括]（[状态]）
- v2 (spec-v2.md): [一句话概括]（[状态]）
- v(N+1) (spec-v(N+1).md): [本次变动概括]（进行中）
```

Update the existing current-version entry with all applicable Plan references, changed scopes and explicit unchanged-scope provenance. Synchronize affected Plan bindings in Step 5.5; unchanged peers may retain valid earlier bindings. Do not create a local INDEX master for a remote tracker. Missing provenance is reported, not guessed from the largest issue number/newest comment.

The current entry must reference this confirmed Spec. Before writes, reread the entry and relevant Plan scope/version/parent facts against Step 1. Do not overwrite concurrent repartitioning or silently drop a peer from the registry; report the actual conflict.

### Step 5.5: Update affected Plans in place

For each affected scope, reuse its actual Plan file/issue and qualified packages:
- Revise the decisions, paths/anchors, risks and simple-Todo decomposition caused by the change. Preserve history and target-creation phases; do not renumber unrelated packages.
- Bind the changed scope to the confirmed new Spec version. Synchronize authorized Parent/navigation changes under the same-feature fresh-read rules; do not force a foreign parent or move historical Todos.
- Add a brief version/change reason. Review new technical choices under actual user/delegated authority; changed scope does not inherit unrelated approval automatically.
- Reset acceptance only for changed functional items, retaining their prior user evidence. Preserve peer approval, accepted scope and completed Todos. Reference-only navigation updates do not reset those states.

For unaffected Plans, record the scope/contract comparison in the current change entry and leave their implementation decisions, approval/acceptance and Todos intact. Do not reopen, re-review or recreate their work merely for the global Spec version bump. A genuinely new independent scope may add a Plan using AI-selected boundaries or the user's explicit count/grouping; do not duplicate or overlap existing current scopes. Repartitioning active/claimed work needs actual ownership reconciliation, not a silent reparent.

New Todos belong to the particular affected/new Plan and its P<N>. Keep approaches in each body; comments hold discussion/evidence.

### Step 6: Add follow-on tickets

Continue local numbering after the highest Todo across the feature, not separately per Plan. Remotely use returned IDs. Backlink each new Todo only in its actual owning Plan/INDEX branch, start ready and preserve historical resolved work.

```
issues/
├── 01-xxx.md  (resolved)
├── 02-xxx.md  (resolved)
├── 03-xxx.md  (resolved)
└── 04-yyy.md  (新，ready)   ← 本次变动
```

Keep Spec provenance separate from the qualified Plan, e.g. `Spec: spec-v2.md`, `Plan: plans/import.md#P1` or the actual remote Plan issue/P<N>. Legacy plan.md remains valid. Preserve explicit small-change omissions. Blockers within a Plan must be real; a new peer-Plan dependency requires revisiting the independent partition rather than hiding it in a Todo.

A new Todo's Parent is its actual Plan or declared fallback, not the old Todo it continues or an arbitrary peer Plan. Maintain real local/native navigation and type labels using only configured Projects. Do not rewrite historical versions, parents or states merely for a Spec change.

### Step 7: Hand off to implementation

Use flow-do for verified eligible Todos in the affected/new Plans. It follows each exact owner, qualified package and applicable scope/version. Unaffected independent Plans can continue under their valid provenance; do not require them to wait for this changed Plan's review or implementation.

## Outputs

- A locatable incremental Spec version and updated current-version/evolution entry.
- A complete current Plan registry with only affected scoped artifacts changed and any justified new independent Plan added.
- New, sequentially numbered tickets with distinct Spec/Plan provenance.

## Boundaries and related stages

Use this for surface/local evolution and traceable history, not a new feature, fundamental redesign, or overwriting history. Fundamental changes return to `/flow-spec`; ready tickets use `/flow-do`. Scout may inspect current code in Step 1 according to execution-mode.
