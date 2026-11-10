---
name: flow-status
description: "Read-only repository or feature progress snapshot with ownership hierarchy, current-versus-history ticket states, closure synchronization, and functional acceptance. Use when resuming work, changing sessions, or handing off context."
---

# Flow Status

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Aggregate progress **read-only**: do not change files, states, commits, or remote data.

## Workflow

### Step 1: Identify tracker and state definitions

Read the [shared contract](../_agents/workflow-contract.md) and `docs/agents/issue-tracker.md`. If the declaration is absent, report uninitialized/request `/flow-init` and stop. Local mode scans `.scratch`; remote mode reads the declared issue source. Report inaccessible data instead of guessing.

Read this tracker's Status values dynamically. New defaults are ready/claimed/resolved/parked; old trackers may declare code-complete. Without a declaration, use the four defaults with a warning. An old intermediate state alone proves neither engineering completion nor functional acceptance.

### Step 2: Discover features

- Locally prefer `.scratch/README.md` links, or scan first-level directories for INDEX/spec/plan/issues. A named feature limits discovery to that feature. Show unregistered legacy work too; do not treat standalone Epic/notes folders as features.
- Follow every current Spec `Plans:` entry or legacy singleton `Plan:`, locally through INDEX and actual files, remotely through declared references/native relationships. Do not silently select the first Plan. Unlisted files are not current merely by name or modification time.
- For complex file discovery, scout may return paths only under execution-mode; the main session determines status. Inline or unavailable scout means direct inspection.

### Step 3: Read authoritative records

Locally inspect:
1. INDEX, if present: current Spec/evolution and real navigation links. Cross-check body fields; the index does not prove ticket state or approval.
2. The referenced Spec; without INDEX use spec.md or latest spec-vN.md.
3. Individual issue files: declared Status, Parent, distinct Spec/Plan, dependencies, title/number. Infer missing Parent only from explicit Plan/Spec, label the inference, and never rewrite it. Support legacy `**来源**:`, `**依赖**:`, `**阻塞**:`; conflicting repeated fields make dependency status unknown, not silently ignored.
4. Each current Plan: actual identity, Parent/Spec/Scope, approval evidence, own Todos and scoped acceptance. Qualify P<N> by its Plan. One Plan owns each Todo; intentionally omitted artifacts remain omitted.
5. Generated contract filenames.
6. Substantive un-ticketed feature documents, such as integration notes: list them without inventing status.

Read all applicable Plan bodies and their own Todo/contract records. Verify scope/version applicability against the current Spec registry/change evidence. An unaffected Plan may retain an earlier binding with explicit unchanged-scope provenance; neither silently accept all older versions nor mark every peer stale after an unrelated Spec change. Report old comment-only plans/missing or conflicting sources without migrating them.

On GitHub, read actual parent/sub-issues and compare them with body references. Use supported APIs when the CLI lacks fields. Permission/query failures are unknown, not evidence of no parent. On GitLab use its actual capabilities. List conflicting sources/values without fixing relationships, labels, or indexes.

Include closed tickets: read linked tickets individually or use queries such as `gh issue list --state all`, not only the default open list. Compare engineering Status and native state separately. Resolved-but-open means engineering complete/closure unsynchronized; closed with missing/failed engineering evidence is a conflict, not proof of passing work.

**State interpretation:**
- Classify declared values by their semantics; missing/out-of-range values are unknown.
- A missing dependency field is no declared blocker, not proof that all dependencies were verified.
- A blocked ready ticket is not executable.
- Do not infer completion from modification times, file counts, or conversation alone.

| Category | Typical values | Meaning |
|----------|----------------|---------|
| done | resolved | Ticket engineering complete; may release ticket dependencies, not proof of human acceptance |
| code-complete | code-complete | Declared legacy intermediate state; preserve its semantics/evidence, never auto-migrate it |
| parked | parked | Awaiting conditions/decision; incomplete and does not release dependencies |
| active | ready / claimed | Available/in progress |
| unknown | Missing/out-of-range | Incomplete state data |

Version continuation is **not Parent ownership**. Historical Todos retain their states; new work belongs to its actual Plan/fallback. Select Next from each Plan's verified applicable scope/version, including explicitly unchanged scope evidence. Do not equate P1 under two Plans or count a peer's completed Todo as this Plan's work. Historical code-complete/parked references are not anomalies merely because they remain open.

**Dependencies:** done releases them under the tracker, with external conditions checked separately. Legacy code-complete releases only when explicitly allowed and supported by engineering evidence; warn that the old ticket is not fully closed. Parked/unknown do not release. Unverifiable external conditions (samples, phase-start approval, etc.) remain warnings/blockers.

### Step 4: Determine stage

Apply this priority to each current Plan's execution layer; list history separately. Report mixed Plan states instead of one misleading global stage. One pending/unapproved/blocked Plan does not make another approved independent scope ineligible. Then summarize Spec coverage, outstanding Plans and distinct global checks; a user-specified count alone does not prove all scopes are covered or approved.

| Condition | Stage |
|-----------|-------|
| No Spec and no tickets | Requirements/planning not started |
| Required referenced Spec/Plan missing without intentional omission | Incomplete state |
| Current plan unapproved | Awaiting plan review; related ready tickets cannot start |
| Current ready/claimed tickets | Implementing |
| Unknown states or conflict with required engineering evidence | Incomplete state; show contradictions |
| Parked/unfinished checks without active work | Engineering blocked/awaiting external conditions |
| Only legacy code-complete and done remain | Legacy engineering verification/closure pending |
| All execution tickets resolved but native closure unsynchronized | Engineering complete/closure sync pending; show acceptance separately |
| All resolved, Acceptance pending | Engineering complete/awaiting functional acceptance |
| All resolved, changes-requested | Functional acceptance requires adjustment/follow-on work |
| All resolved, accepted with applicable-scope user evidence | Functionally accepted |
| All resolved, both Spec/Plan intentionally omitted | Engineering complete/no independent functional acceptance declared |
| All resolved, acceptance state/evidence missing | Engineering complete/acceptance record incomplete |
| No tickets, Spec without plan | Awaiting blueprint or intentional small-ticket path |
| No tickets, plan unapproved | Awaiting plan review |
| No tickets, plan approved | Awaiting ticketing |

Explicit none/reason with complete small-ticket decisions is valid. Plan approval comes from its stamp and applicable user/delegated review evidence, not native closed state. Show a claimed ticket's executor; multiple claims get a concurrency notice.

### Step 5: Report

First emit clickable **Hierarchy**: Epic → Spec → all current peer Plans → each Plan's own Todos. Include each scope/applicable Spec version and per-Plan approval, engineering/closure and acceptance facts from their owners. Preserve legacy names and discover both todo/ticket aliases. Omit intentionally absent levels; P<N> is internal grouping. Label inferred or unsynchronized native relationships rather than presenting them as verified.

Then report separate categories/current-versus-history counts. Native child-close percentages do not replace engineering or acceptance state. Snapshot example:

```text
Feature: <feature>
Tracker: local markdown / GitHub / GitLab
Stage: <阶段>
Spec: <当前 spec 文件/issue 版本引用或 unknown>
Plans: <每个现行 Plan 引用、Scope、适用 Spec 版本及批准状态；旧单 Plan 亦可>
Acceptance: <逐 Plan 范围及 Spec 全局项的真实入口／状态，不能由数量推断>
Closure sync: <本地 resolved 即关闭；或远程 closed / 关闭未同步 / unknown>

Progress: <n> resolved / <n> code-complete / <n> parked / <n> active / <n> unknown（共 <total>）

Todos（待办，按归类排序）:
- [resolved] 01: <title>
- [code-complete] 19: <title>  ← legacy intermediate state
- [parked] 22: <title>  ← 外部依赖未到位
- [claimed] 23: <title>  ← in progress
- [ready] 24: <title>
- [unknown] 05: <title>

Blocked:
- 12 blocked by 10（10 为 resolved，票级依赖已解除）
- 21 外部依赖：算法侧 golden 样张（无法验证）

Contracts:
- <ticket-contract-file>

Next:
- <按实际 Plan 分组列出依赖已解除、方案已批准的可执行 ready Todos；明确省略 plan 时按简化规则>
- 老版本遗留的 ready 照列但标注其外部阻塞，不冒充“立即能做”
- 没有可执行 Todo 时明确说明原因

Warnings:
- <missing INDEX / unknown Status / multiple claimed / tracker unavailable
   / plan 待 review 未批准 / 旧中间态缺少工程证据 / parked 未解除下游 / 外部依赖无法验证
   / 上层功能待验收或缺少验收记录 / 工程完成但关闭未同步 / 父单 closed 但未记录功能验收
   / Parent 与原生关系冲突 / 索引缺失或链接失效 / 原生关系未同步
   / 发现未建票的实质文档（建议建票，如 backend-integration.md）>
```

Without a named feature, begin with a short feature table, then expand the current active feature:

```text
Feature                         Stage       Progress                              Next
blog-comments                   实现中       2/4 resolved                          03-nested-replies
payment                         待功能验收   3/3 resolved                          Plan 功能验收
user-export                     功能已验收   3/3 resolved                          无
grid-chain                      状态不完整   1/3 resolved + 1 unknown              检查 unknown Status
```

## Constraints

This is an observation view, not a state manager. Never edit records to make progress look complete. Keep legacy intermediates, engineering/closure, per-Plan approval, Git authorization and scoped human acceptance distinct. Show verified eligible groups per Plan rather than arbitrarily choosing one; explain unknown ownership/provenance or the absence of eligible work. Recommend a Todo for substantive untracked work without creating it.
