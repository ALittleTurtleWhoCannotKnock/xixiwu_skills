---
name: amend
description: "Handle confirmed changes to an implemented feature with an incremental Spec version, current-version index, the same updated plan, and follow-on tickets. Check whether the change actually requires redesign; keep the interactive decisions in the main session."
---

# Amend

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Evolve an implemented feature incrementally from its existing Spec rather than restarting the entire workflow.

## When to use

- Existing Spec/tickets were implemented and committed.
- Fields, behavior, boundaries, or local requirements change.
- Repeating the complete requirements workflow would be disproportionate.

## Core disciplines

1. Ask only about the changed part.
2. Distinguish an increment from a redesign; small patches must not conceal a fundamental change.
3. Freeze old Specs; write a separate version such as spec-v2.md.
4. Use the latest execution version, referring to history as needed.
5. Update the same local plan.md or independent Plan issue body, not plan-vN or Spec comments.
6. Before classifying depth, briefly steelman the change's true intent: restate it, examine both directions, and find decisive variables. Apply the global AGENTS.md significance criteria, including architecture, scope, cross-module impact, alternatives, user behavior, and irreversibility.

## Workflow

### Step 1: Read current state

Read the [shared contract](../_agents/workflow-contract.md), tracker, and execution-mode (missing defaults to subagent for later scout work).

Locally inspect `.scratch/<feature>/INDEX.md` if present, the current spec.md/spec-vN.md, and existing issue numbers. Remotely read the current Spec version, independent Plan, and tickets; verify the tracker's current-version reference against the Plan's `Spec:`. Missing `.scratch` does not mean a remote Spec is absent. If neither mode has a locatable Spec, use the normal requirements workflow.

### Step 2: Discuss only the change

Do not repeat unchanged requirements. Example:

```
当前 spec-vN 的方案是 X。你说要变动，具体变什么？

- 哪个决策/模块/字段要改？
- 改成什么？
- 为什么变？（新需求 / 原方案有问题 / 外部约束变了）
```

### Step 3: Confirm depth

Classify the change and present the judgment:

| Depth | Signals | Action |
|-------|---------|--------|
| Surface | Fields, copy, boundary checks, defaults | New Spec version and follow-on tickets |
| Local | One implementation choice, library, or module responsibility | Incremental version and tickets |
| Fundamental | Architectural assumptions, main flow, non-goals, or most decisions overturned | Stop incremental work and recommend `/to-spec` |

For a fundamental change, explain the concrete issue, for example:

```
这个变动动摇了 spec 的核心决策（具体：[哪条]）。
在原 spec 上打补丁会在烂地基上续建。
建议：重新走 /to-spec 生成全新 spec。
仍要强制增量吗？（不推荐）
```

Continue only after the user's confirmation.

### Step 4: Write the next Spec

For an increment, create local `spec-v(N+1).md`; remotely retain the tracker's existing version-storage convention and older references. Do not silently change how versions are stored.

```markdown
# <Feature> Spec v(N+1)

Parent: <沿用已确认的 Epic；没有则 none>
Plan: <既有 Plan 文件/issue 引用；没有则 none>

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

**当前版本**: [spec-v(N+1).md](spec-v(N+1).md)（agent 实现一律读这个）

Plan: [plan.md](plan.md)（仅已有 Plan 时保留此链接）

## 层级
[保留既有链接，标记当前规格及历史票版本；Step 6 保存新票后追加其真实链接，不重复保存状态]

## 演进
- v1 (spec.md): [一句话概括]（[状态]）
- v2 (spec-v2.md): [一句话概括]（[状态]）
- v(N+1) (spec-v(N+1).md): [本次变动概括]（进行中）
```

Remotely update the existing current-version entry and synchronize the Plan's `Spec:` in Step 5.5. Do not create a local INDEX master. If version provenance cannot be located, report it rather than guessing from the newest comment or largest issue number.

The current entry must reference this confirmed Spec. Before writing, reread INDEX/the remote current-version entry and the Plan's `Spec:`; compare with Step 1. On concurrent changes, stop overwriting and report both values.

### Step 5.5: Update the same plan

Update the same plan.md or independent Plan issue body:
- Revise affected technical decisions and explain which v(N+1) change caused them.
- Revise affected package paths/risks and update method anchors as symbols move. Preserve anchors as the location source; append new package numbers rather than renumbering history.
- Even if only product boundaries changed, update the Plan's `Spec:` to the new version.
- The new Spec inherits the confirmed Epic; synchronize the Plan's `Parent:`. For a new GitHub Spec issue, verify the old parent and same-feature evidence under the shared migration rule before moving the same Plan. Report conflicts without forcing a reparent or moving old tickets.
- Add the lightweight change stamp `> 更新：v(N+1) [日期] [一句话]`, preserving history while the body stays current.
- When functional acceptance scope changes, reset the sole acceptance owner (Plan, otherwise Spec) to pending, retaining prior version records. Engineering tickets still close automatically; earlier accepted state is not acceptance of the new scope.

New tickets reference this same plan and P<N>. Preserve target-creation phases. Reuse valid approval for the current approach; review out-of-scope new technical choices before updating approval. Comments hold discussion/evidence, not the authoritative plan.

### Step 6: Add follow-on tickets

Locally continue numbering after the highest existing ticket; remotely use returned issue numbers and backlink them in the same Plan. Start at `Status: ready` and preserve old resolved tickets.

```
issues/
├── 01-xxx.md  (resolved)
├── 02-xxx.md  (resolved)
├── 03-xxx.md  (resolved)
└── 04-yyy.md  (新，ready)   ← 本次变动
```

Keep `Spec:` and `Plan:` separate: locally `spec-v(N+1).md` / `plan.md#P<N>`, remotely the Spec-version reference / Plan issue and P<N>. If a plan is unnecessary, declare `Plan: none (原因)` and include necessary decisions. Use `Blocked by:` for dependencies.

A new ticket's `Parent:` is the same Plan or the shared fallback, **not the old ticket it continues**. Maintain local INDEX/root navigation or remote native relationships/type labels. Use only a configured Project. Do not rewrite historical ticket versions, parents, or states because the current Spec changed.

### Step 7: Hand off to implementation

Use `/implement` when new tickets are ready. It reads INDEX/the remote current reference, checks the Plan's `Spec:`, and uses v(N+1), referring back to v(N) for context.

## Outputs

- A locatable incremental Spec version and updated current-version/evolution entry.
- The same plan updated in place.
- New, sequentially numbered tickets with distinct Spec/Plan provenance.

## Boundaries and related stages

Use this for surface/local evolution and traceable history, not a new feature, fundamental redesign, or overwriting history. Fundamental changes return to `/to-spec`; ready tickets use `/implement`. Scout may inspect current code in Step 1 according to execution-mode.
